#!/usr/bin/env python3
"""
Check available date ranges for backtesting.
Shows when bar data and feature data are available for each instrument.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Instrument, Bar, Feature
from datetime import date


def check_available_dates():
    """Check and display available date ranges."""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("AVAILABLE DATE RANGES FOR BACKTESTING")
        print("=" * 80)
        print()
        
        instruments = db.query(Instrument).filter(Instrument.active == True).all()
        
        if not instruments:
            print("❌ No instruments found in database.")
            print("   Run: make setup")
            return
        
        for instrument in instruments:
            print(f"📊 {instrument.symbol} - {instrument.name}")
            print("-" * 80)
            
            # Check bars
            bars = db.query(Bar).filter(
                Bar.instrument_id == instrument.id
            ).order_by(Bar.date).all()
            
            if bars:
                bar_start = bars[0].date
                bar_end = bars[-1].date
                bar_count = len(bars)
                print(f"  Bar Data:     {bar_start} to {bar_end} ({bar_count} bars)")
            else:
                print(f"  Bar Data:     ❌ No data")
                print()
                continue
            
            # Check features
            features = db.query(Feature).filter(
                Feature.instrument_id == instrument.id
            ).order_by(Feature.date).all()
            
            if features:
                feature_start = features[0].date
                feature_end = features[-1].date
                feature_count = len(features)
                print(f"  Feature Data: {feature_start} to {feature_end} ({feature_count} features)")
                
                # Calculate the warmup period
                if bars and features:
                    warmup_days = (feature_start - bar_start).days
                    print(f"  Warmup:       {warmup_days} days (bars before features are available)")
                
                print()
                print(f"  ✅ BACKTEST RANGE: {feature_start} to {feature_end}")
                print(f"     Use these dates in Strategy Lab for {instrument.symbol}")
            else:
                print(f"  Feature Data: ❌ No features computed")
                print(f"     Run: curl -X POST http://localhost:8432/features/recompute-all")
            
            print()
        
        print("=" * 80)
        print("💡 TIP:")
        print("   Features require historical data for calculation:")
        print("   - MA(50) needs 50 days of bars")
        print("   - ATR(20) needs 20 days of bars")
        print("   - The first features appear after the longest lookback period")
        print()
        print("   To backtest from an earlier date, you need bar data starting")
        print("   at least 50 days before your desired backtest start date.")
        print("=" * 80)
        
    finally:
        db.close()


if __name__ == "__main__":
    check_available_dates()

