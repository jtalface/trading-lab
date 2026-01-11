"""Event-driven backtest engine."""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from app.models import (
    Instrument, Bar, Feature, BacktestRun, Signal, Order, Fill, 
    Position, PortfolioSnapshot, SignalType, OrderSide, OrderStatus
)
from app.schemas import BacktestConfig
from app.engines.feature_engine import FeatureEngine
from app.engines.strategy_engine import (
    StrategyEngine, StrategyConfig, PositionState, 
    TrendDirection, SignalAction
)
from app.engines.risk_engine import RiskEngine, RiskConfig, RiskMode


@dataclass
class BacktestPosition:
    """Position tracking during backtest."""
    instrument_id: int
    symbol: str
    quantity: int  # Positive for long, negative for short
    entry_price: float
    entry_date: date
    stop_price: float
    multiplier: float
    
    def get_value(self, current_price: float) -> float:
        """Calculate current position value."""
        return self.quantity * current_price * self.multiplier
    
    def get_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L."""
        return self.quantity * (current_price - self.entry_price) * self.multiplier


@dataclass
class BacktestState:
    """Complete backtest state."""
    equity: float
    cash: float
    peak_equity: float
    positions: Dict[int, BacktestPosition] = field(default_factory=dict)
    
    # Track per-instrument state for strategy cooldowns
    strategy_states: Dict[int, PositionState] = field(default_factory=dict)
    
    # Track daily start equity for daily loss calculation
    start_of_day_equity: float = 0
    
    # Metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    gross_profit: float = 0
    gross_loss: float = 0


class BacktestEngine:
    """
    Event-driven backtest engine with realistic fills.
    
    Features:
    - Daily bar event loop
    - Entry at next open with configurable slippage
    - Stop checks using high/low
    - Position sizing via risk engine
    - Comprehensive metrics calculation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.feature_engine = FeatureEngine()
    
    def run_backtest(
        self,
        backtest_run: BacktestRun,
        config: BacktestConfig
    ) -> BacktestRun:
        """
        Execute backtest and store results.
        
        Args:
            backtest_run: BacktestRun database object
            config: Backtest configuration
        
        Returns:
            Updated BacktestRun with results
        """
        try:
            backtest_run.status = "running"
            self.db.commit()
            
            # Initialize engines
            strategy_config = StrategyConfig(
                atr_period=config.atr_period,
                ma_period=config.ma_period,
                ma_slope_period=config.ma_slope_period,
                breakout_period=config.breakout_period,
                exit_period=config.exit_period,
                stop_atr_multiple=config.stop_atr_multiple,
                cooldown_days=config.cooldown_days
            )
            
            risk_config = RiskConfig(
                risk_per_trade=config.risk_per_trade,
                max_contracts_per_instrument=config.max_contracts_per_instrument,
                max_gross_exposure=config.max_gross_exposure,
                max_correlated_exposure=config.max_correlated_exposure,
                drawdown_warning_pct=config.drawdown_warning_pct,
                drawdown_halt_pct=config.drawdown_halt_pct,
                daily_loss_limit_pct=config.daily_loss_limit_pct
            )
            
            strategy_engine = StrategyEngine(strategy_config)
            risk_engine = RiskEngine(risk_config)
            
            # Fetch instruments
            instruments = self.db.query(Instrument).filter(
                Instrument.symbol.in_(config.instruments),
                Instrument.active == True
            ).all()
            
            if not instruments:
                raise ValueError(f"No active instruments found for symbols: {config.instruments}")
            
            # Prepare data for each instrument
            instrument_data = {}
            for instrument in instruments:
                df = self.feature_engine.get_features_dataframe(
                    self.db, instrument, config.start_date, config.end_date
                )
                if df.empty:
                    print(f"Warning: No data found for {instrument.symbol}")
                    continue
                
                # Features are pre-calculated, so we just need at least 2 days (current + previous)
                if len(df) < 2:
                    print(f"Warning: Need at least 2 days of data for {instrument.symbol}, have {len(df)}")
                    continue
                    
                instrument_data[instrument.id] = {
                    'instrument': instrument,
                    'data': df
                }
                print(f"Loaded {len(df)} bars for {instrument.symbol}")
            
            if not instrument_data:
                raise ValueError("No data available for selected instruments and date range")
            
            # Get all unique dates across instruments
            all_dates = sorted(set(
                date for data in instrument_data.values()
                for date in data['data'].index
            ))
            
            # Initialize backtest state
            state = BacktestState(
                equity=config.initial_capital,
                cash=config.initial_capital,
                peak_equity=config.initial_capital,
                start_of_day_equity=config.initial_capital
            )
            
            # Initialize strategy states for each instrument
            for inst_id in instrument_data.keys():
                state.strategy_states[inst_id] = PositionState()
            
            # Event loop - process each date
            print(f"\nProcessing {len(all_dates)} trading days...")
            for i, current_date in enumerate(all_dates):
                state = self._process_day(
                    current_date=current_date,
                    state=state,
                    instrument_data=instrument_data,
                    strategy_engine=strategy_engine,
                    risk_engine=risk_engine,
                    config=config,
                    backtest_run=backtest_run
                )
                
                # Commit periodically (every 10 days) to avoid large transactions
                if (i + 1) % 10 == 0:
                    self.db.commit()
                    print(f"  Processed {i + 1}/{len(all_dates)} days, Equity: ${state.equity:,.2f}")
            
            # Final commit before calculating metrics
            self.db.commit()
            print(f"Completed processing. Final equity: ${state.equity:,.2f}")
            print(f"Total trades: {state.total_trades}")
            
            # Calculate final metrics
            self._calculate_final_metrics(backtest_run, state, all_dates)
            
            backtest_run.status = "completed"
            backtest_run.completed_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            backtest_run.status = "failed"
            backtest_run.error_message = str(e)
            self.db.commit()
            raise
        
        return backtest_run
    
    def _process_day(
        self,
        current_date: date,
        state: BacktestState,
        instrument_data: Dict,
        strategy_engine: StrategyEngine,
        risk_engine: RiskEngine,
        config: BacktestConfig,
        backtest_run: BacktestRun
    ) -> BacktestState:
        """Process a single trading day."""
        # Set start of day equity for daily loss calculation
        state.start_of_day_equity = state.equity
        
        # Update position values and check stops
        state = self._update_positions_and_check_stops(
            current_date, state, instrument_data, config, backtest_run
        )
        
        # Generate signals for each instrument
        for inst_id, data_dict in instrument_data.items():
            instrument = data_dict['instrument']
            df = data_dict['data']
            
            if current_date not in df.index:
                continue
            
            # Get current and previous bar
            current_idx = df.index.get_loc(current_date)
            if current_idx == 0:
                continue  # Need previous bar
            
            current_row = df.loc[current_date]
            prev_row = df.iloc[current_idx - 1]
            
            current_bar = {
                'open': current_row['open'],
                'high': current_row['high'],
                'low': current_row['low'],
                'close': current_row['close']
            }
            
            prev_bar = {
                'open': prev_row['open'],
                'high': prev_row['high'],
                'low': prev_row['low'],
                'close': prev_row['close']
            }
            
            features = {
                'atr_20': current_row['atr_20'],
                'ma_50': current_row['ma_50'],
                'ma_slope_10': current_row['ma_slope_10'],
                'hh_20': prev_row['hh_20'],  # Use previous day's HH for breakout detection
                'll_20': prev_row['ll_20'],  # Use previous day's LL for breakout detection
                'hh_10': current_row['hh_10'],  # Use current day's HH10 for exit detection (includes today's range)
                'll_10': current_row['ll_10']   # Use current day's LL10 for exit detection (includes today's range)
            }
            
            # Generate signal
            strategy_signal = strategy_engine.generate_signal(
                current_date=current_date,
                current_bar=current_bar,
                prev_bar=prev_bar,
                features=features,
                position=state.strategy_states[inst_id]
            )
            print(f"  signal: {strategy_signal.action.value}, reason: {strategy_signal.reason}")
            
            # Process signal
            state = self._process_signal(
                strategy_signal, instrument, current_date, state,
                risk_engine, config, backtest_run, df
            )
        
        # Calculate daily P&L and create snapshot
        state = self._create_daily_snapshot(current_date, state, backtest_run, instrument_data)
        
        return state
    
    def _update_positions_and_check_stops(
        self,
        current_date: date,
        state: BacktestState,
        instrument_data: Dict,
        config: BacktestConfig,
        backtest_run: BacktestRun
    ) -> BacktestState:
        """Update position values and check for stop hits."""
        positions_to_close = []
        
        for inst_id, position in state.positions.items():
            if inst_id not in instrument_data:
                continue
            
            df = instrument_data[inst_id]['data']
            if current_date not in df.index:
                continue
            
            current_row = df.loc[current_date]
            
            # Check if stop was hit using high/low
            stop_hit = False
            if position.quantity > 0:  # Long position
                stop_hit = current_row['low'] <= position.stop_price
                exit_price = position.stop_price if stop_hit else current_row['close']
            else:  # Short position
                stop_hit = current_row['high'] >= position.stop_price
                exit_price = position.stop_price if stop_hit else current_row['close']
            
            if stop_hit:
                # Exit position at stop
                state = self._execute_exit(
                    current_date=current_date,
                    instrument_id=inst_id,
                    position=position,
                    exit_price=exit_price,
                    reason="stop_hit",
                    state=state,
                    config=config,
                    backtest_run=backtest_run
                )
                positions_to_close.append(inst_id)
        
        # Remove closed positions
        for inst_id in positions_to_close:
            del state.positions[inst_id]
        
        return state
    
    def _process_signal(
        self,
        signal,
        instrument: Instrument,
        current_date: date,
        state: BacktestState,
        risk_engine: RiskEngine,
        config: BacktestConfig,
        backtest_run: BacktestRun,
        df: pd.DataFrame
    ) -> BacktestState:
        """Process a strategy signal and execute trades."""
        # Store signal in database
        if signal.action not in [SignalAction.HOLD, SignalAction.NO_ACTION]:
            db_signal = Signal(
                instrument_id=instrument.id,
                backtest_run_id=backtest_run.id,
                date=current_date,
                signal_type=self._map_signal_type(signal.action),
                price=signal.price,
                stop_price=signal.stop_price,
                reason=signal.reason
            )
            self.db.add(db_signal)
        
        # Handle exits
        if signal.action in [SignalAction.EXIT_LONG, SignalAction.EXIT_SHORT,
                            SignalAction.STOP_LONG, SignalAction.STOP_SHORT]:
            if instrument.id in state.positions:
                position = state.positions[instrument.id]
                state = self._execute_exit(
                    current_date=current_date,
                    instrument_id=instrument.id,
                    position=position,
                    exit_price=signal.price,
                    reason="signal_exit",
                    state=state,
                    config=config,
                    backtest_run=backtest_run
                )
                del state.positions[instrument.id]
                
                # Update strategy state
                state.strategy_states[instrument.id].last_exit_date = current_date
                state.strategy_states[instrument.id].last_exit_direction = \
                    TrendDirection.LONG if signal.action in [SignalAction.EXIT_LONG, SignalAction.STOP_LONG] else TrendDirection.SHORT
                state.strategy_states[instrument.id].direction = None
        
        # Handle entries
        elif signal.action in [SignalAction.ENTRY_LONG, SignalAction.ENTRY_SHORT]:
            # Calculate position size
            current_positions = [
                {
                    'value': p.get_value(signal.price),
                    'symbol': p.symbol
                }
                for p in state.positions.values()
            ]
            
            position_size, risk_state = risk_engine.validate_trade(
                equity=state.equity,
                peak_equity=state.peak_equity,
                daily_pnl=state.equity - state.start_of_day_equity,
                start_of_day_equity=state.start_of_day_equity,
                entry_price=signal.price,
                stop_price=signal.stop_price,
                tick_size=instrument.tick_size,
                multiplier=instrument.multiplier,
                current_positions=current_positions,
                instrument_symbol=instrument.symbol
            )
            
            if position_size.contracts > 0:
                # Get next day's open for entry (if available)
                next_date = self._get_next_trading_day(current_date, df)
                if next_date is not None:
                    next_row = df.loc[next_date]
                    entry_price = next_row['open']
                    
                    # Apply slippage
                    slippage_dollars = config.slippage_ticks * instrument.tick_size
                    if signal.action == SignalAction.ENTRY_LONG:
                        entry_price += slippage_dollars
                        quantity = position_size.contracts
                    else:
                        entry_price -= slippage_dollars
                        quantity = -position_size.contracts
                    
                    # Execute entry
                    state = self._execute_entry(
                        entry_date=next_date,
                        instrument=instrument,
                        quantity=quantity,
                        entry_price=entry_price,
                        stop_price=signal.stop_price,
                        state=state,
                        config=config,
                        backtest_run=backtest_run
                    )
                    
                    # Update strategy state
                    state.strategy_states[instrument.id].direction = \
                        TrendDirection.LONG if signal.action == SignalAction.ENTRY_LONG else TrendDirection.SHORT
                    state.strategy_states[instrument.id].entry_price = entry_price
                    state.strategy_states[instrument.id].entry_date = next_date
                    state.strategy_states[instrument.id].stop_price = signal.stop_price
                    state.strategy_states[instrument.id].contracts = position_size.contracts
            
            # Update signal with target contracts
            if hasattr(self.db, 'query'):  # Update the last signal we created
                latest_signal = self.db.query(Signal).filter(
                    Signal.instrument_id == instrument.id,
                    Signal.backtest_run_id == backtest_run.id,
                    Signal.date == current_date
                ).order_by(Signal.id.desc()).first()
                if latest_signal:
                    latest_signal.target_contracts = position_size.contracts
        
        return state
    
    def _execute_entry(
        self,
        entry_date: date,
        instrument: Instrument,
        quantity: int,
        entry_price: float,
        stop_price: float,
        state: BacktestState,
        config: BacktestConfig,
        backtest_run: BacktestRun
    ) -> BacktestState:
        """Execute entry trade."""
        # Create order
        order = Order(
            instrument_id=instrument.id,
            backtest_run_id=backtest_run.id,
            order_date=entry_date,
            side=OrderSide.BUY if quantity > 0 else OrderSide.SELL,
            quantity=abs(quantity),
            order_type="MARKET",
            status=OrderStatus.FILLED
        )
        self.db.add(order)
        self.db.flush()
        
        # Create fill
        commission = config.commission_per_contract * abs(quantity)
        fill = Fill(
            order_id=order.id,
            backtest_run_id=backtest_run.id,
            fill_date=entry_date,
            fill_price=entry_price,
            quantity=abs(quantity),
            commission=commission,
            slippage=config.slippage_ticks
        )
        self.db.add(fill)
        
        # Update state
        position = BacktestPosition(
            instrument_id=instrument.id,
            symbol=instrument.symbol,
            quantity=quantity,
            entry_price=entry_price,
            entry_date=entry_date,
            stop_price=stop_price,
            multiplier=instrument.multiplier
        )
        state.positions[instrument.id] = position
        
        # Update cash (for futures, only deduct commission, not notional value)
        # Futures use margin, not full capital deployment like stocks
        state.cash -= commission
        
        return state
    
    def _execute_exit(
        self,
        current_date: date,
        instrument_id: int,
        position: BacktestPosition,
        exit_price: float,
        reason: str,
        state: BacktestState,
        config: BacktestConfig,
        backtest_run: BacktestRun
    ) -> BacktestState:
        """Execute exit trade."""
        # Create order
        order = Order(
            instrument_id=instrument_id,
            backtest_run_id=backtest_run.id,
            order_date=current_date,
            side=OrderSide.SELL if position.quantity > 0 else OrderSide.BUY,
            quantity=abs(position.quantity),
            order_type="MARKET",
            status=OrderStatus.FILLED
        )
        self.db.add(order)
        self.db.flush()
        
        # Create fill
        commission = config.commission_per_contract * abs(position.quantity)
        fill = Fill(
            order_id=order.id,
            backtest_run_id=backtest_run.id,
            fill_date=current_date,
            fill_price=exit_price,
            quantity=abs(position.quantity),
            commission=commission,
            slippage=config.slippage_ticks
        )
        self.db.add(fill)
        
        # Calculate P&L
        realized_pnl = position.get_pnl(exit_price)
        net_pnl = realized_pnl - commission
        
        # Update metrics
        state.total_trades += 1
        if net_pnl > 0:
            state.winning_trades += 1
            state.gross_profit += net_pnl
        else:
            state.losing_trades += 1
            state.gross_loss += abs(net_pnl)
        
        # Update cash (for futures, add realized P&L minus commission)
        state.cash += realized_pnl - commission
        
        # Remove position from tracking
        del state.positions[instrument_id]
        
        return state
    
    def _create_daily_snapshot(
        self,
        current_date: date,
        state: BacktestState,
        backtest_run: BacktestRun,
        instrument_data: Dict = None
    ) -> BacktestState:
        """Create daily portfolio snapshot."""
        # Calculate unrealized P&L using current close prices
        unrealized_pnl = 0.0
        total_exposure = 0.0
        
        if instrument_data:
            for inst_id, position in state.positions.items():
                if inst_id in instrument_data:
                    df = instrument_data[inst_id]['data']
                    if current_date in df.index:
                        current_close = df.loc[current_date]['close']
                        unrealized_pnl += position.get_pnl(current_close)
                        total_exposure += abs(position.get_value(current_close))
        
        # Update equity to include unrealized P&L
        state.equity = state.cash + unrealized_pnl
        
        # Update peak equity
        if state.equity > state.peak_equity:
            state.peak_equity = state.equity
        
        # Calculate drawdown
        drawdown = (state.peak_equity - state.equity) / state.peak_equity if state.peak_equity > 0 else 0
        
        # Daily P&L
        daily_pnl = state.equity - state.start_of_day_equity
        
        # Create snapshot
        snapshot = PortfolioSnapshot(
            backtest_run_id=backtest_run.id,
            date=current_date,
            equity=state.equity,
            cash=state.cash,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=state.gross_profit - state.gross_loss,
            daily_pnl=daily_pnl,
            drawdown=drawdown,
            total_exposure=total_exposure,
            num_positions=len(state.positions)
        )
        self.db.add(snapshot)
        
        return state
    
    def _calculate_final_metrics(
        self,
        backtest_run: BacktestRun,
        state: BacktestState,
        all_dates: List[date]
    ):
        """Calculate final backtest metrics."""
        # Fetch all snapshots
        snapshots = self.db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.backtest_run_id == backtest_run.id
        ).order_by(PortfolioSnapshot.date).all()
        
        if not snapshots:
            return
        
        # Calculate returns
        equity_series = pd.Series([s.equity for s in snapshots])
        returns = equity_series.pct_change().dropna()
        
        # Basic metrics
        backtest_run.final_equity = state.equity
        backtest_run.total_return = (state.equity - backtest_run.initial_capital) / backtest_run.initial_capital
        
        # CAGR
        years = (all_dates[-1] - all_dates[0]).days / 365.25
        if years > 0:
            backtest_run.cagr = (state.equity / backtest_run.initial_capital) ** (1 / years) - 1
        
        # Sharpe Ratio (assuming 252 trading days)
        if len(returns) > 1:
            backtest_run.sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 1:
            downside_std = downside_returns.std()
            backtest_run.sortino_ratio = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        
        # Max Drawdown
        drawdowns = [s.drawdown for s in snapshots]
        backtest_run.max_drawdown = max(drawdowns) if drawdowns else 0
        
        # Max Drawdown Duration
        in_drawdown = False
        dd_start = None
        max_dd_days = 0
        for i, dd in enumerate(drawdowns):
            if dd > 0 and not in_drawdown:
                in_drawdown = True
                dd_start = i
            elif dd == 0 and in_drawdown:
                in_drawdown = False
                dd_days = i - dd_start
                max_dd_days = max(max_dd_days, dd_days)
        backtest_run.max_drawdown_duration = max_dd_days
        
        # Trade metrics
        backtest_run.total_trades = state.total_trades
        backtest_run.win_rate = state.winning_trades / state.total_trades if state.total_trades > 0 else 0
        backtest_run.profit_factor = state.gross_profit / state.gross_loss if state.gross_loss > 0 else 0
    
    @staticmethod
    def _map_signal_type(signal_action: SignalAction) -> SignalType:
        """Map SignalAction to SignalType."""
        mapping = {
            SignalAction.ENTRY_LONG: SignalType.ENTRY_LONG,
            SignalAction.ENTRY_SHORT: SignalType.ENTRY_SHORT,
            SignalAction.EXIT_LONG: SignalType.EXIT_LONG,
            SignalAction.EXIT_SHORT: SignalType.EXIT_SHORT,
            SignalAction.STOP_LONG: SignalType.STOP_LONG,
            SignalAction.STOP_SHORT: SignalType.STOP_SHORT,
        }
        return mapping.get(signal_action)
    
    @staticmethod
    def _get_next_trading_day(current_date: date, df: pd.DataFrame) -> Optional[date]:
        """Get next available trading day from dataframe."""
        dates = df.index.tolist()
        try:
            current_idx = dates.index(current_date)
            if current_idx < len(dates) - 1:
                return dates[current_idx + 1]
        except ValueError:
            pass
        return None

