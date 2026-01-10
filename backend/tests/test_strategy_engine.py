"""Tests for strategy engine."""
import pytest
from datetime import date

from app.engines.strategy_engine import (
    StrategyEngine, StrategyConfig, PositionState,
    TrendDirection, SignalAction
)


class TestStrategyEngine:
    """Test suite for StrategyEngine."""
    
    def test_check_trend_filter_long(self):
        """Test long trend filter."""
        engine = StrategyEngine()
        
        # Long conditions: close > MA50 and slope > 0
        trend = engine.check_trend_filter(
            close=100,
            ma_50=95,
            ma_slope_10=0.5
        )
        
        assert trend == TrendDirection.LONG
    
    def test_check_trend_filter_short(self):
        """Test short trend filter."""
        engine = StrategyEngine()
        
        # Short conditions: close < MA50 and slope < 0
        trend = engine.check_trend_filter(
            close=100,
            ma_50=105,
            ma_slope_10=-0.5
        )
        
        assert trend == TrendDirection.SHORT
    
    def test_check_trend_filter_neutral(self):
        """Test neutral trend filter."""
        engine = StrategyEngine()
        
        # Neutral: close > MA50 but slope < 0
        trend = engine.check_trend_filter(
            close=100,
            ma_50=95,
            ma_slope_10=-0.5
        )
        
        assert trend == TrendDirection.NEUTRAL
    
    def test_check_breakout_entry_long(self):
        """Test long breakout entry."""
        engine = StrategyEngine()
        
        # Close breaks above HH20
        signal = engine.check_breakout_entry(
            close=105,
            prev_close=99,
            hh_20=100,
            ll_20=80,
            trend=TrendDirection.LONG
        )
        
        assert signal == SignalAction.ENTRY_LONG
    
    def test_check_breakout_entry_short(self):
        """Test short breakout entry."""
        engine = StrategyEngine()
        
        # Close breaks below LL20
        signal = engine.check_breakout_entry(
            close=79,
            prev_close=85,
            hh_20=100,
            ll_20=80,
            trend=TrendDirection.SHORT
        )
        
        assert signal == SignalAction.ENTRY_SHORT
    
    def test_check_exit_signal_long(self):
        """Test long exit signal."""
        engine = StrategyEngine()
        
        # Close crosses below LL10
        signal = engine.check_exit_signal(
            close=89,
            ll_10=90,
            hh_10=100,
            position_direction=TrendDirection.LONG
        )
        
        assert signal == SignalAction.EXIT_LONG
    
    def test_check_exit_signal_short(self):
        """Test short exit signal."""
        engine = StrategyEngine()
        
        # Close crosses above HH10
        signal = engine.check_exit_signal(
            close=101,
            ll_10=90,
            hh_10=100,
            position_direction=TrendDirection.SHORT
        )
        
        assert signal == SignalAction.EXIT_SHORT
    
    def test_check_stop_hit_long(self):
        """Test long stop hit."""
        engine = StrategyEngine()
        
        # Low touches stop
        hit = engine.check_stop_hit(
            high=105,
            low=94,
            stop_price=95,
            position_direction=TrendDirection.LONG
        )
        
        assert hit == True
    
    def test_check_stop_not_hit_long(self):
        """Test long stop not hit."""
        engine = StrategyEngine()
        
        # Low doesn't touch stop
        hit = engine.check_stop_hit(
            high=105,
            low=96,
            stop_price=95,
            position_direction=TrendDirection.LONG
        )
        
        assert hit == False
    
    def test_calculate_stop_price_long(self):
        """Test stop price calculation for long."""
        engine = StrategyEngine()
        
        stop = engine.calculate_stop_price(
            entry_price=100,
            atr=5,
            direction=TrendDirection.LONG
        )
        
        # Stop should be 2*ATR below entry (default multiplier)
        assert stop == 100 - (2 * 5)
    
    def test_calculate_stop_price_short(self):
        """Test stop price calculation for short."""
        engine = StrategyEngine()
        
        stop = engine.calculate_stop_price(
            entry_price=100,
            atr=5,
            direction=TrendDirection.SHORT
        )
        
        # Stop should be 2*ATR above entry
        assert stop == 100 + (2 * 5)
    
    def test_is_in_cooldown(self):
        """Test cooldown period check."""
        engine = StrategyEngine()
        
        # Exit on day 1, try to enter on day 2 (within 3-day cooldown)
        in_cooldown = engine.is_in_cooldown(
            current_date=date(2023, 1, 3),
            last_exit_date=date(2023, 1, 1),
            last_exit_direction=TrendDirection.LONG,
            entry_direction=TrendDirection.LONG
        )
        
        assert in_cooldown == True
    
    def test_not_in_cooldown_different_direction(self):
        """Test no cooldown for opposite direction."""
        engine = StrategyEngine()
        
        # Exit long, try to enter short (different direction)
        in_cooldown = engine.is_in_cooldown(
            current_date=date(2023, 1, 3),
            last_exit_date=date(2023, 1, 1),
            last_exit_direction=TrendDirection.LONG,
            entry_direction=TrendDirection.SHORT
        )
        
        assert in_cooldown == False
    
    def test_generate_signal_entry(self):
        """Test signal generation for entry."""
        engine = StrategyEngine()
        position = PositionState()
        
        current_bar = {'open': 100, 'high': 105, 'low': 99, 'close': 105}
        prev_bar = {'open': 98, 'high': 102, 'low': 97, 'close': 99}
        features = {
            'atr_20': 5.0,
            'ma_50': 95.0,
            'ma_slope_10': 0.5,
            'hh_20': 100.0,
            'll_20': 80.0,
            'hh_10': 98.0,
            'll_10': 85.0,
        }
        
        signal = engine.generate_signal(
            current_date=date(2023, 1, 10),
            current_bar=current_bar,
            prev_bar=prev_bar,
            features=features,
            position=position
        )
        
        # Should generate long entry signal
        assert signal.action == SignalAction.ENTRY_LONG
        assert signal.stop_price is not None
        assert signal.stop_price < signal.price

