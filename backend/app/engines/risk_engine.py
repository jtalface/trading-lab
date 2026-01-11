"""Risk management engine for position sizing and guardrails."""
import math
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class RiskMode(Enum):
    """Risk mode based on drawdown."""
    NORMAL = "normal"
    WARNING = "warning"  # Drawdown > 10%
    HALT = "halt"  # Drawdown > 15% or daily loss > 2%


@dataclass
class RiskConfig:
    """Risk management configuration."""
    risk_per_trade: float = 0.005  # 0.5% of equity
    max_contracts_per_instrument: Optional[int] = None
    max_gross_exposure: Optional[float] = None  # As fraction of equity
    max_correlated_exposure: Optional[float] = None  # For ES+NQ combined
    
    # Drawdown guardrails
    drawdown_warning_pct: float = 0.10  # 10%
    drawdown_halt_pct: float = 0.15  # 15%
    daily_loss_limit_pct: float = 0.02  # 2%


@dataclass
class PositionSize:
    """Calculated position size."""
    contracts: int
    risk_amount: float
    stop_distance_points: float
    stop_distance_dollars: float
    reason: str


@dataclass
class RiskState:
    """Current risk state of the portfolio."""
    equity: float
    peak_equity: float
    daily_pnl: float
    drawdown_pct: float
    daily_loss_pct: float
    mode: RiskMode
    risk_multiplier: float  # Adjusted risk based on drawdown
    can_open_new_trades: bool
    message: str


class RiskEngine:
    """
    Risk management engine.
    
    Features:
    - Position sizing based on equity and stop distance
    - Drawdown-based risk adjustment
    - Position and exposure limits
    - Daily loss limits
    """
    
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
    
    def calculate_risk_state(
        self,
        current_equity: float,
        peak_equity: float,
        daily_pnl: float,
        start_of_day_equity: float
    ) -> RiskState:
        """
        Calculate current risk state and mode.
        
        Args:
            current_equity: Current portfolio equity
            peak_equity: All-time peak equity
            daily_pnl: Today's P&L
            start_of_day_equity: Equity at start of day
        
        Returns:
            RiskState with mode and risk multiplier
        """
        # Calculate drawdown
        drawdown_pct = (peak_equity - current_equity) / peak_equity if peak_equity > 0 else 0
        
        # Calculate daily loss percentage
        daily_loss_pct = daily_pnl / start_of_day_equity if start_of_day_equity > 0 else 0
        
        # Determine risk mode
        mode = RiskMode.NORMAL
        risk_multiplier = 1.0
        can_open_new_trades = True
        message = "Normal operations"
        
        # Check daily loss limit
        if daily_loss_pct < -self.config.daily_loss_limit_pct:
            mode = RiskMode.HALT
            risk_multiplier = 0.0
            can_open_new_trades = False
            message = f"Daily loss limit exceeded ({daily_loss_pct:.2%}). No new trades today."
        
        # Check drawdown limits
        elif drawdown_pct >= self.config.drawdown_halt_pct:
            mode = RiskMode.HALT
            risk_multiplier = 0.0
            can_open_new_trades = False
            message = f"Max drawdown exceeded ({drawdown_pct:.2%}). Risk-off mode."
        
        elif drawdown_pct >= self.config.drawdown_warning_pct:
            mode = RiskMode.WARNING
            risk_multiplier = 0.5  # Halve risk
            can_open_new_trades = True
            message = f"Drawdown warning ({drawdown_pct:.2%}). Risk reduced to 50%."
        
        return RiskState(
            equity=current_equity,
            peak_equity=peak_equity,
            daily_pnl=daily_pnl,
            drawdown_pct=drawdown_pct,
            daily_loss_pct=daily_loss_pct,
            mode=mode,
            risk_multiplier=risk_multiplier,
            can_open_new_trades=can_open_new_trades,
            message=message
        )
    
    def calculate_position_size(
        self,
        equity: float,
        entry_price: float,
        stop_price: float,
        tick_size: float,
        multiplier: float,
        risk_state: RiskState
    ) -> PositionSize:
        """
        Calculate position size based on risk per trade.
        
        Args:
            equity: Current portfolio equity
            entry_price: Entry price
            stop_price: Stop loss price
            tick_size: Contract tick size
            multiplier: Contract multiplier (point value)
            risk_state: Current risk state
        
        Returns:
            PositionSize with contract quantity and details
        """
        # Calculate stop distance in points
        stop_distance_points = abs(entry_price - stop_price)
        
        # Calculate stop distance in dollars per contract
        stop_distance_dollars = stop_distance_points * multiplier
        
        if stop_distance_dollars <= 0:
            return PositionSize(
                contracts=0,
                risk_amount=0,
                stop_distance_points=0,
                stop_distance_dollars=0,
                reason="Invalid stop distance"
            )
        
        # Calculate base risk amount
        base_risk_amount = equity * self.config.risk_per_trade
        
        # Adjust for risk state
        adjusted_risk_amount = base_risk_amount * risk_state.risk_multiplier
        
        if adjusted_risk_amount <= 0:
            return PositionSize(
                contracts=0,
                risk_amount=0,
                stop_distance_points=stop_distance_points,
                stop_distance_dollars=stop_distance_dollars,
                reason=f"Risk halted: {risk_state.message}"
            )
        
        # Calculate number of contracts
        contracts_float = adjusted_risk_amount / stop_distance_dollars
        contracts = int(math.floor(contracts_float))
        print(f"DEBUG RISK: stop_dist_points={stop_distance_points:.2f}, stop_dist_$={stop_distance_dollars:.2f}")
        print(f"DEBUG RISK: risk_amt={adjusted_risk_amount:.2f}, contracts_float={contracts_float:.4f}, contracts={contracts}")
        
        # Apply max contracts per instrument limit
        if self.config.max_contracts_per_instrument is not None:
            if contracts > self.config.max_contracts_per_instrument:
                contracts = self.config.max_contracts_per_instrument
                reason = f"Limited to max {self.config.max_contracts_per_instrument} contracts per instrument"
            else:
                reason = "Normal sizing"
        else:
            reason = "Normal sizing"
        
        # Ensure at least 0 contracts
        contracts = max(0, contracts)
        
        return PositionSize(
            contracts=contracts,
            risk_amount=adjusted_risk_amount,
            stop_distance_points=stop_distance_points,
            stop_distance_dollars=stop_distance_dollars,
            reason=reason
        )
    
    def check_exposure_limits(
        self,
        current_positions: List[Dict],
        new_position_value: float,
        equity: float,
        instrument_symbol: str = None
    ) -> Tuple[bool, str]:
        """
        Check if adding a new position would exceed exposure limits.
        
        Args:
            current_positions: List of dicts with 'value' and 'symbol' keys
            new_position_value: Value of new position to add
            equity: Current equity
            instrument_symbol: Symbol of new position (for correlation check)
        
        Returns:
            (allowed, reason)
        """
        # Calculate total current exposure
        total_current_exposure = sum(abs(p['value']) for p in current_positions)
        total_new_exposure = total_current_exposure + abs(new_position_value)
        
        print(f"DEBUG EXPOSURE: current=${total_current_exposure:,.2f}, new=${new_position_value:,.2f}, total=${total_new_exposure:,.2f}")
        
        # Check max gross exposure
        if self.config.max_gross_exposure is not None:
            max_exposure_dollars = equity * self.config.max_gross_exposure
            print(f"DEBUG EXPOSURE: equity=${equity:,.2f}, max_gross={self.config.max_gross_exposure}, max_allowed=${max_exposure_dollars:,.2f}")
            print(f"DEBUG EXPOSURE: Check: {total_new_exposure:,.2f} > {max_exposure_dollars:,.2f}? {total_new_exposure > max_exposure_dollars}")
            if total_new_exposure > max_exposure_dollars:
                return False, f"Would exceed max gross exposure ({self.config.max_gross_exposure:.1%} of equity)"
        
        # Check correlated exposure (ES + NQ)
        if self.config.max_correlated_exposure is not None and instrument_symbol:
            correlated_symbols = {'ES', 'NQ'}  # E-mini S&P and Nasdaq
            
            if instrument_symbol in correlated_symbols:
                # Calculate combined ES+NQ exposure
                correlated_exposure = sum(
                    abs(p['value']) for p in current_positions 
                    if p.get('symbol') in correlated_symbols
                )
                correlated_exposure += abs(new_position_value)
                
                max_correlated_dollars = equity * self.config.max_correlated_exposure
                if correlated_exposure > max_correlated_dollars:
                    return False, f"Would exceed max correlated exposure for ES+NQ ({self.config.max_correlated_exposure:.1%})"
        
        return True, "Within exposure limits"
    
    def validate_trade(
        self,
        equity: float,
        peak_equity: float,
        daily_pnl: float,
        start_of_day_equity: float,
        entry_price: float,
        stop_price: float,
        tick_size: float,
        multiplier: float,
        current_positions: List[Dict] = None,
        instrument_symbol: str = None
    ) -> Tuple[PositionSize, RiskState]:
        """
        Validate a trade and calculate position size.
        
        Returns:
            (PositionSize, RiskState)
        """
        # Calculate risk state
        risk_state = self.calculate_risk_state(
            equity, peak_equity, daily_pnl, start_of_day_equity
        )
        
        # If we can't open new trades, return 0 size
        if not risk_state.can_open_new_trades:
            return PositionSize(
                contracts=0,
                risk_amount=0,
                stop_distance_points=abs(entry_price - stop_price),
                stop_distance_dollars=abs(entry_price - stop_price) * multiplier,
                reason=risk_state.message
            ), risk_state
        
        # Calculate position size
        position_size = self.calculate_position_size(
            equity, entry_price, stop_price, tick_size, multiplier, risk_state
        )
        
        # Check exposure limits if we have current positions
        if current_positions is not None and position_size.contracts > 0:
            position_value = position_size.contracts * entry_price * multiplier
            print(f"DEBUG RISK: Checking exposure limits, position_value=${position_value:,.2f}")
            allowed, reason = self.check_exposure_limits(
                current_positions, position_value, equity, instrument_symbol
            )
            print(f"DEBUG RISK: Exposure check: allowed={allowed}, reason={reason}")
            
            if not allowed:
                print(f"DEBUG RISK: ❌ TRADE REJECTED BY EXPOSURE LIMITS!")
                position_size.contracts = 0
                position_size.reason = reason
        
        print(f"DEBUG RISK: Returning contracts={position_size.contracts}")
        return position_size, risk_state

