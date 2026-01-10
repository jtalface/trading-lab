"""Strategy engine implementing breakout trend-following logic."""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import date, timedelta
from dataclasses import dataclass
from enum import Enum


class TrendDirection(Enum):
    """Trend direction enum."""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class SignalAction(Enum):
    """Signal action enum."""
    ENTRY_LONG = "entry_long"
    ENTRY_SHORT = "entry_short"
    EXIT_LONG = "exit_long"
    EXIT_SHORT = "exit_short"
    STOP_LONG = "stop_long"
    STOP_SHORT = "stop_short"
    HOLD = "hold"
    NO_ACTION = "no_action"


@dataclass
class StrategyConfig:
    """Strategy configuration parameters."""
    atr_period: int = 20
    ma_period: int = 50
    ma_slope_period: int = 10
    breakout_period: int = 20
    exit_period: int = 10
    stop_atr_multiple: float = 2.0
    cooldown_days: int = 3


@dataclass
class PositionState:
    """Current position state."""
    direction: Optional[TrendDirection] = None
    entry_price: float = 0.0
    entry_date: Optional[date] = None
    stop_price: float = 0.0
    contracts: int = 0
    last_exit_date: Optional[date] = None
    last_exit_direction: Optional[TrendDirection] = None


@dataclass
class StrategySignal:
    """Strategy signal output."""
    date: date
    action: SignalAction
    price: float
    stop_price: Optional[float] = None
    reason: str = ""
    
    # Additional context
    trend_direction: Optional[TrendDirection] = None
    atr: Optional[float] = None
    ma_value: Optional[float] = None
    ma_slope: Optional[float] = None


class StrategyEngine:
    """
    Breakout Trend Following Strategy v1
    
    Rules:
    - Long filter: Close > MA50 and Slope50 > 0
    - Short filter: Close < MA50 and Slope50 < 0
    - Entry: Close breaks above HH20 (long) or below LL20 (short)
    - Initial stop: 2 * ATR20 away from entry
    - Exit: Close crosses LL10 (exit long) or HH10 (exit short)
    - Catastrophe stop enforced using high/low
    - Cooldown: 3 trading days after exit before re-entry same direction
    """
    
    def __init__(self, config: StrategyConfig = None):
        self.config = config or StrategyConfig()
    
    def check_trend_filter(
        self,
        close: float,
        ma_50: float,
        ma_slope_10: float
    ) -> TrendDirection:
        """Check if trend filter conditions are met."""
        if pd.isna(ma_50) or pd.isna(ma_slope_10):
            return TrendDirection.NEUTRAL
        
        if close > ma_50 and ma_slope_10 > 0:
            return TrendDirection.LONG
        elif close < ma_50 and ma_slope_10 < 0:
            return TrendDirection.SHORT
        else:
            return TrendDirection.NEUTRAL
    
    def check_breakout_entry(
        self,
        close: float,
        prev_close: float,
        hh_20: float,
        ll_20: float,
        trend: TrendDirection
    ) -> Optional[SignalAction]:
        """Check for breakout entry signals."""
        if pd.isna(hh_20) or pd.isna(ll_20):
            return None
        
        # Long breakout: close breaks above HH20
        if trend == TrendDirection.LONG and close > hh_20 and prev_close <= hh_20:
            return SignalAction.ENTRY_LONG
        
        # Short breakout: close breaks below LL20
        if trend == TrendDirection.SHORT and close < ll_20 and prev_close >= ll_20:
            return SignalAction.ENTRY_SHORT
        
        return None
    
    def check_exit_signal(
        self,
        close: float,
        ll_10: float,
        hh_10: float,
        position_direction: TrendDirection
    ) -> Optional[SignalAction]:
        """Check for exit signals based on LL10/HH10 cross."""
        if pd.isna(ll_10) or pd.isna(hh_10):
            return None
        
        # Exit long: close crosses below LL10
        if position_direction == TrendDirection.LONG and close < ll_10:
            return SignalAction.EXIT_LONG
        
        # Exit short: close crosses above HH10
        if position_direction == TrendDirection.SHORT and close > hh_10:
            return SignalAction.EXIT_SHORT
        
        return None
    
    def check_stop_hit(
        self,
        high: float,
        low: float,
        stop_price: float,
        position_direction: TrendDirection
    ) -> bool:
        """Check if catastrophe stop was hit using high/low."""
        if position_direction == TrendDirection.LONG:
            return low <= stop_price
        elif position_direction == TrendDirection.SHORT:
            return high >= stop_price
        return False
    
    def calculate_stop_price(
        self,
        entry_price: float,
        atr: float,
        direction: TrendDirection
    ) -> float:
        """Calculate initial stop price."""
        stop_distance = self.config.stop_atr_multiple * atr
        
        if direction == TrendDirection.LONG:
            return entry_price - stop_distance
        else:  # SHORT
            return entry_price + stop_distance
    
    def is_in_cooldown(
        self,
        current_date: date,
        last_exit_date: Optional[date],
        last_exit_direction: Optional[TrendDirection],
        entry_direction: TrendDirection
    ) -> bool:
        """Check if we're in cooldown period for this direction."""
        if not last_exit_date or not last_exit_direction:
            return False
        
        # Only apply cooldown if trying to re-enter same direction
        if last_exit_direction != entry_direction:
            return False
        
        days_since_exit = (current_date - last_exit_date).days
        return days_since_exit < self.config.cooldown_days
    
    def generate_signal(
        self,
        current_date: date,
        current_bar: Dict,
        prev_bar: Optional[Dict],
        features: Dict,
        position: PositionState
    ) -> StrategySignal:
        """
        Generate trading signal for current bar.
        
        Args:
            current_date: Current date
            current_bar: Dict with 'open', 'high', 'low', 'close'
            prev_bar: Previous bar data (None on first bar)
            features: Dict with technical features
            position: Current position state
        
        Returns:
            StrategySignal with action and details
        """
        close = current_bar['close']
        high = current_bar['high']
        low = current_bar['low']
        
        atr = features.get('atr_20')
        ma_50 = features.get('ma_50')
        ma_slope_10 = features.get('ma_slope_10')
        hh_20 = features.get('hh_20')
        ll_20 = features.get('ll_20')
        hh_10 = features.get('hh_10')
        ll_10 = features.get('ll_10')
        
        # Check if we have a position
        has_position = position.direction is not None
        
        # If we have a position, check stops and exits first
        if has_position:
            # Check catastrophe stop
            if self.check_stop_hit(high, low, position.stop_price, position.direction):
                return StrategySignal(
                    date=current_date,
                    action=SignalAction.STOP_LONG if position.direction == TrendDirection.LONG else SignalAction.STOP_SHORT,
                    price=position.stop_price,
                    reason=f"Catastrophe stop hit at {position.stop_price:.2f}",
                    atr=atr,
                    ma_value=ma_50,
                    ma_slope=ma_slope_10
                )
            
            # Check exit signal
            exit_signal = self.check_exit_signal(close, ll_10, hh_10, position.direction)
            if exit_signal:
                return StrategySignal(
                    date=current_date,
                    action=exit_signal,
                    price=close,
                    reason=f"Exit signal: close crossed {'LL10' if position.direction == TrendDirection.LONG else 'HH10'}",
                    atr=atr,
                    ma_value=ma_50,
                    ma_slope=ma_slope_10
                )
            
            # Hold position
            return StrategySignal(
                date=current_date,
                action=SignalAction.HOLD,
                price=close,
                reason="Holding position",
                trend_direction=position.direction,
                atr=atr,
                ma_value=ma_50,
                ma_slope=ma_slope_10
            )
        
        # No position - check for entry signals
        
        # Need previous bar to detect breakout
        if not prev_bar:
            return StrategySignal(
                date=current_date,
                action=SignalAction.NO_ACTION,
                price=close,
                reason="No previous bar data",
                atr=atr,
                ma_value=ma_50,
                ma_slope=ma_slope_10
            )
        
        prev_close = prev_bar['close']
        
        # Check trend filter
        trend = self.check_trend_filter(close, ma_50, ma_slope_10)
        
        if trend == TrendDirection.NEUTRAL:
            return StrategySignal(
                date=current_date,
                action=SignalAction.NO_ACTION,
                price=close,
                reason="No clear trend (neutral filter)",
                trend_direction=trend,
                atr=atr,
                ma_value=ma_50,
                ma_slope=ma_slope_10
            )
        
        # Check for breakout entry
        entry_signal = self.check_breakout_entry(close, prev_close, hh_20, ll_20, trend)
        
        if not entry_signal:
            return StrategySignal(
                date=current_date,
                action=SignalAction.NO_ACTION,
                price=close,
                reason=f"Trend {trend.value} but no breakout",
                trend_direction=trend,
                atr=atr,
                ma_value=ma_50,
                ma_slope=ma_slope_10
            )
        
        # Check cooldown
        entry_direction = TrendDirection.LONG if entry_signal == SignalAction.ENTRY_LONG else TrendDirection.SHORT
        if self.is_in_cooldown(current_date, position.last_exit_date, position.last_exit_direction, entry_direction):
            days_left = self.config.cooldown_days - (current_date - position.last_exit_date).days
            return StrategySignal(
                date=current_date,
                action=SignalAction.NO_ACTION,
                price=close,
                reason=f"In cooldown period ({days_left} days remaining)",
                trend_direction=trend,
                atr=atr,
                ma_value=ma_50,
                ma_slope=ma_slope_10
            )
        
        # Generate entry signal with stop
        stop_price = self.calculate_stop_price(close, atr, entry_direction)
        
        return StrategySignal(
            date=current_date,
            action=entry_signal,
            price=close,
            stop_price=stop_price,
            reason=f"Breakout entry: close broke {'above HH20' if entry_direction == TrendDirection.LONG else 'below LL20'}",
            trend_direction=trend,
            atr=atr,
            ma_value=ma_50,
            ma_slope=ma_slope_10
        )
    
    def backtest_single_instrument(
        self,
        df: pd.DataFrame,
        initial_position: PositionState = None
    ) -> pd.DataFrame:
        """
        Run strategy logic over historical data for a single instrument.
        
        Args:
            df: DataFrame with columns: date (index), open, high, low, close, 
                atr_20, ma_50, ma_slope_10, hh_20, ll_20, hh_10, ll_10
            initial_position: Starting position state
        
        Returns:
            DataFrame with additional columns for signals and actions
        """
        position = initial_position or PositionState()
        signals = []
        
        df_sorted = df.sort_index()
        
        for i, (date_val, row) in enumerate(df_sorted.iterrows()):
            current_bar = {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close']
            }
            
            prev_bar = None
            if i > 0:
                prev_row = df_sorted.iloc[i - 1]
                prev_bar = {
                    'open': prev_row['open'],
                    'high': prev_row['high'],
                    'low': prev_row['low'],
                    'close': prev_row['close']
                }
            
            features = {
                'atr_20': row['atr_20'],
                'ma_50': row['ma_50'],
                'ma_slope_10': row['ma_slope_10'],
                'hh_20': row['hh_20'],
                'll_20': row['ll_20'],
                'hh_10': row['hh_10'],
                'll_10': row['ll_10']
            }
            
            signal = self.generate_signal(
                date_val, current_bar, prev_bar, features, position
            )
            
            # Update position state based on signal
            if signal.action in [SignalAction.ENTRY_LONG, SignalAction.ENTRY_SHORT]:
                position.direction = TrendDirection.LONG if signal.action == SignalAction.ENTRY_LONG else TrendDirection.SHORT
                position.entry_price = signal.price
                position.entry_date = signal.date
                position.stop_price = signal.stop_price
            
            elif signal.action in [SignalAction.EXIT_LONG, SignalAction.EXIT_SHORT, 
                                   SignalAction.STOP_LONG, SignalAction.STOP_SHORT]:
                position.last_exit_date = signal.date
                position.last_exit_direction = position.direction
                position.direction = None
                position.entry_price = 0.0
                position.entry_date = None
                position.stop_price = 0.0
            
            signals.append(signal)
        
        # Create results DataFrame
        results_df = df_sorted.copy()
        results_df['signal_action'] = [s.action.value for s in signals]
        results_df['signal_price'] = [s.price for s in signals]
        results_df['stop_price'] = [s.stop_price for s in signals]
        results_df['signal_reason'] = [s.reason for s in signals]
        
        return results_df

