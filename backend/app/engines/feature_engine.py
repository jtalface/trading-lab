"""Feature computation engine for technical indicators."""
import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import date
from sqlalchemy.orm import Session
from app.models import Bar, Feature, Instrument


class FeatureEngine:
    """Computes and persists technical features."""
    
    @staticmethod
    def compute_atr(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Compute Average True Range."""
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def compute_ma(df: pd.DataFrame, period: int = 50) -> pd.Series:
        """Compute Moving Average."""
        return df['close'].rolling(window=period).mean()
    
    @staticmethod
    def compute_ma_slope(ma: pd.Series, period: int = 10) -> pd.Series:
        """Compute slope of moving average over specified period."""
        # Linear regression slope over last N points
        slopes = []
        for i in range(len(ma)):
            if i < period - 1:
                slopes.append(np.nan)
            else:
                y = ma.iloc[i - period + 1:i + 1].values
                if pd.isna(y).any():
                    slopes.append(np.nan)
                else:
                    x = np.arange(period)
                    # Use polyfit for simple linear regression
                    coeffs = np.polyfit(x, y, 1)
                    slopes.append(coeffs[0])  # Slope coefficient
        
        return pd.Series(slopes, index=ma.index)
    
    @staticmethod
    def compute_highest_high(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Compute highest high over specified period."""
        return df['high'].rolling(window=period).max()
    
    @staticmethod
    def compute_lowest_low(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Compute lowest low over specified period."""
        return df['low'].rolling(window=period).min()
    
    def compute_all_features(
        self,
        df: pd.DataFrame,
        atr_period: int = 20,
        ma_period: int = 50,
        ma_slope_period: int = 10,
        breakout_period: int = 20,
        exit_period: int = 10
    ) -> pd.DataFrame:
        """Compute all features for a dataframe of bars."""
        result = df.copy()
        
        # Compute features
        result['atr_20'] = self.compute_atr(df, atr_period)
        result['ma_50'] = self.compute_ma(df, ma_period)
        result['ma_slope_10'] = self.compute_ma_slope(result['ma_50'], ma_slope_period)
        result['hh_20'] = self.compute_highest_high(df, breakout_period)
        result['ll_20'] = self.compute_lowest_low(df, breakout_period)
        result['hh_10'] = self.compute_highest_high(df, exit_period)
        result['ll_10'] = self.compute_lowest_low(df, exit_period)
        
        return result
    
    def recompute_features_for_instrument(
        self,
        db: Session,
        instrument: Instrument,
        atr_period: int = 20,
        ma_period: int = 50,
        ma_slope_period: int = 10,
        breakout_period: int = 20,
        exit_period: int = 10
    ) -> int:
        """
        Recompute all features for an instrument.
        Returns number of features computed.
        """
        # Fetch all bars for instrument
        bars = db.query(Bar).filter(
            Bar.instrument_id == instrument.id
        ).order_by(Bar.date).all()
        
        if not bars:
            return 0
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'date': bar.date,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        } for bar in bars])
        
        df = df.set_index('date')
        
        # Compute features
        features_df = self.compute_all_features(
            df, atr_period, ma_period, ma_slope_period, breakout_period, exit_period
        )
        
        # Delete existing features for this instrument
        db.query(Feature).filter(
            Feature.instrument_id == instrument.id
        ).delete()
        
        # Insert new features
        feature_count = 0
        for date_val, row in features_df.iterrows():
            # Skip rows with NaN values in critical features
            if pd.isna(row['atr_20']) or pd.isna(row['ma_50']):
                continue
            
            feature = Feature(
                instrument_id=instrument.id,
                date=date_val,
                atr_20=float(row['atr_20']) if not pd.isna(row['atr_20']) else None,
                ma_50=float(row['ma_50']) if not pd.isna(row['ma_50']) else None,
                ma_slope_10=float(row['ma_slope_10']) if not pd.isna(row['ma_slope_10']) else None,
                hh_20=float(row['hh_20']) if not pd.isna(row['hh_20']) else None,
                ll_20=float(row['ll_20']) if not pd.isna(row['ll_20']) else None,
                hh_10=float(row['hh_10']) if not pd.isna(row['hh_10']) else None,
                ll_10=float(row['ll_10']) if not pd.isna(row['ll_10']) else None,
            )
            db.add(feature)
            feature_count += 1
        
        db.commit()
        return feature_count
    
    def get_features_dataframe(
        self,
        db: Session,
        instrument: Instrument,
        start_date: date = None,
        end_date: date = None
    ) -> pd.DataFrame:
        """Get features as a pandas DataFrame."""
        query = db.query(Bar, Feature).join(
            Feature,
            (Bar.instrument_id == Feature.instrument_id) & (Bar.date == Feature.date)
        ).filter(Bar.instrument_id == instrument.id)
        
        if start_date:
            query = query.filter(Bar.date >= start_date)
        if end_date:
            query = query.filter(Bar.date <= end_date)
        
        query = query.order_by(Bar.date)
        
        results = query.all()
        
        if not results:
            return pd.DataFrame()
        
        data = []
        for bar, feature in results:
            data.append({
                'date': bar.date,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume,
                'atr_20': feature.atr_20,
                'ma_50': feature.ma_50,
                'ma_slope_10': feature.ma_slope_10,
                'hh_20': feature.hh_20,
                'll_20': feature.ll_20,
                'hh_10': feature.hh_10,
                'll_10': feature.ll_10,
            })
        
        df = pd.DataFrame(data)
        df = df.set_index('date')
        return df

