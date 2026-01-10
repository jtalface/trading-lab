"""Check database status and available data."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Instrument, Bar, Feature


def check_data():
    """Check what data is available in the database."""
    db = SessionLocal()
    
    print("=" * 60)
    print("DATABASE STATUS CHECK")
    print("=" * 60)
    
    # Check instruments
    instruments = db.query(Instrument).all()
    print(f"\n📊 Instruments: {len(instruments)}")
    if instruments:
        for inst in instruments:
            print(f"  - {inst.symbol}: {inst.name}")
    else:
        print("  ⚠️  No instruments found!")
        print("  Run: python scripts/seed_data.py")
    
    # Check bars
    print(f"\n📈 Bar Data:")
    for inst in instruments:
        bar_count = db.query(Bar).filter(Bar.instrument_id == inst.id).count()
        print(f"  - {inst.symbol}: {bar_count} bars")
        
        if bar_count > 0:
            first_bar = db.query(Bar).filter(
                Bar.instrument_id == inst.id
            ).order_by(Bar.date).first()
            last_bar = db.query(Bar).filter(
                Bar.instrument_id == inst.id
            ).order_by(Bar.date.desc()).first()
            print(f"    Range: {first_bar.date} to {last_bar.date}")
    
    # Check features
    print(f"\n🔬 Feature Data:")
    for inst in instruments:
        feature_count = db.query(Feature).filter(Feature.instrument_id == inst.id).count()
        print(f"  - {inst.symbol}: {feature_count} features")
        
        if feature_count > 0:
            first_feature = db.query(Feature).filter(
                Feature.instrument_id == inst.id
            ).order_by(Feature.date).first()
            last_feature = db.query(Feature).filter(
                Feature.instrument_id == inst.id
            ).order_by(Feature.date.desc()).first()
            print(f"    Range: {first_feature.date} to {last_feature.date}")
    
    print("\n" + "=" * 60)
    
    # Recommendations
    total_bars = db.query(Bar).count()
    total_features = db.query(Feature).count()
    
    if len(instruments) == 0:
        print("\n⚠️  ACTION REQUIRED:")
        print("1. Seed instruments: python scripts/seed_data.py")
    elif total_bars == 0:
        print("\n⚠️  ACTION REQUIRED:")
        print("1. Ingest bar data:")
        print("   python scripts/ingest_csv.py ES /app/data/sample_data/ES_sample.csv")
        print("   python scripts/ingest_csv.py NQ /app/data/sample_data/NQ_sample.csv")
    elif total_features == 0:
        print("\n⚠️  ACTION REQUIRED:")
        print("1. Recompute features:")
        print("   curl -X POST http://localhost:8432/features/recompute-all")
    else:
        print("\n✅ Database is ready for backtesting!")
        print(f"   Instruments: {len(instruments)}")
        print(f"   Total bars: {total_bars}")
        print(f"   Total features: {total_features}")
    
    db.close()


if __name__ == "__main__":
    check_data()

