"""Tests for feature engine."""
import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta

from app.engines.feature_engine import FeatureEngine


def create_sample_data(n_bars=100):
    """Create sample bar data for testing."""
    dates = [date(2023, 1, 1) + timedelta(days=i) for i in range(n_bars)]
    
    # Create synthetic price data
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(n_bars) * 2)
    high = close + np.random.rand(n_bars) * 3
    low = close - np.random.rand(n_bars) * 3
    open_price = close + np.random.randn(n_bars)
    
    df = pd.DataFrame({
        'date': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': np.random.randint(1000, 5000, n_bars)
    })
    
    df.set_index('date', inplace=True)
    return df


class TestFeatureEngine:
    """Test suite for FeatureEngine."""
    
    def test_compute_atr(self):
        """Test ATR calculation."""
        engine = FeatureEngine()
        df = create_sample_data(50)
        
        atr = engine.compute_atr(df, period=20)
        
        # Check that ATR is computed
        assert not atr.isna().all()
        
        # ATR should be positive
        assert (atr.dropna() > 0).all()
        
        # First 19 values should be NaN (need 20 bars)
        assert atr.iloc[:19].isna().all()
    
    def test_compute_ma(self):
        """Test moving average calculation."""
        engine = FeatureEngine()
        df = create_sample_data(100)
        
        ma = engine.compute_ma(df, period=50)
        
        # Check that MA is computed
        assert not ma.isna().all()
        
        # First 49 values should be NaN
        assert ma.iloc[:49].isna().all()
        
        # MA should be close to close prices
        assert abs(ma.iloc[-1] - df['close'].iloc[-50:].mean()) < 0.01
    
    def test_compute_ma_slope(self):
        """Test MA slope calculation."""
        engine = FeatureEngine()
        df = create_sample_data(100)
        
        ma = engine.compute_ma(df, period=50)
        slope = engine.compute_ma_slope(ma, period=10)
        
        # Check that slope is computed
        assert not slope.isna().all()
        
        # Slope can be positive or negative
        assert slope.dropna().shape[0] > 0
    
    def test_compute_highest_high(self):
        """Test highest high calculation."""
        engine = FeatureEngine()
        df = create_sample_data(50)
        
        hh = engine.compute_highest_high(df, period=20)
        
        # Check that HH is computed
        assert not hh.isna().all()
        
        # HH should be >= close
        valid_idx = ~hh.isna()
        assert (hh[valid_idx] >= df.loc[valid_idx, 'high']).all()
    
    def test_compute_lowest_low(self):
        """Test lowest low calculation."""
        engine = FeatureEngine()
        df = create_sample_data(50)
        
        ll = engine.compute_lowest_low(df, period=20)
        
        # Check that LL is computed
        assert not ll.isna().all()
        
        # LL should be <= close
        valid_idx = ~ll.isna()
        assert (ll[valid_idx] <= df.loc[valid_idx, 'low']).all()
    
    def test_compute_all_features(self):
        """Test computing all features together."""
        engine = FeatureEngine()
        df = create_sample_data(100)
        
        result = engine.compute_all_features(df)
        
        # Check all features are present
        assert 'atr_20' in result.columns
        assert 'ma_50' in result.columns
        assert 'ma_slope_10' in result.columns
        assert 'hh_20' in result.columns
        assert 'll_20' in result.columns
        assert 'hh_10' in result.columns
        assert 'll_10' in result.columns
        
        # Check that some values are computed (not all NaN)
        for col in ['atr_20', 'ma_50', 'hh_20', 'll_20']:
            assert not result[col].isna().all()

