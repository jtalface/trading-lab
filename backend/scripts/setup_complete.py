"""Complete setup: seed, ingest, and verify data."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_data import seed_instruments
from ingest_csv import ingest_csv
from check_data import check_data


def main():
    """Run complete setup."""
    print("=" * 60)
    print("VOLATILITY EDGE LAB - COMPLETE SETUP")
    print("=" * 60)
    
    # Step 1: Seed instruments
    print("\n[1/3] Seeding instruments...")
    seed_instruments()
    
    # Step 2: Ingest ES data
    print("\n[2/3] Ingesting sample data...")
    print("\n  Loading ES data...")
    ingest_csv(
        symbol='ES',
        csv_path='/app/data/sample_data/ES_sample.csv'
    )
    
    print("\n  Loading NQ data...")
    ingest_csv(
        symbol='NQ',
        csv_path='/app/data/sample_data/NQ_sample.csv'
    )
    
    # Step 3: Verify
    print("\n[3/3] Verifying setup...")
    check_data()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nYou can now:")
    print("  • Run demo backtest: python scripts/run_demo_backtest.py")
    print("  • Access frontend: http://localhost:3847")
    print("  • Access API docs: http://localhost:8432/docs")


if __name__ == "__main__":
    main()

