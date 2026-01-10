"""Seed database with sample instruments and data."""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Instrument


def seed_instruments():
    """Create sample futures instruments."""
    db = SessionLocal()
    
    instruments = [
        {
            "symbol": "ES",
            "name": "E-mini S&P 500",
            "exchange": "CME",
            "tick_size": 0.25,
            "multiplier": 50.0,
            "currency": "USD"
        },
        {
            "symbol": "NQ",
            "name": "E-mini NASDAQ-100",
            "exchange": "CME",
            "tick_size": 0.25,
            "multiplier": 20.0,
            "currency": "USD"
        },
        {
            "symbol": "YM",
            "name": "E-mini Dow",
            "exchange": "CBOT",
            "tick_size": 1.0,
            "multiplier": 5.0,
            "currency": "USD"
        },
        {
            "symbol": "RTY",
            "name": "E-mini Russell 2000",
            "exchange": "CME",
            "tick_size": 0.10,
            "multiplier": 50.0,
            "currency": "USD"
        },
        {
            "symbol": "CL",
            "name": "Crude Oil",
            "exchange": "NYMEX",
            "tick_size": 0.01,
            "multiplier": 1000.0,
            "currency": "USD"
        },
        {
            "symbol": "GC",
            "name": "Gold",
            "exchange": "COMEX",
            "tick_size": 0.10,
            "multiplier": 100.0,
            "currency": "USD"
        },
    ]
    
    created = 0
    for inst_data in instruments:
        # Check if exists
        existing = db.query(Instrument).filter(
            Instrument.symbol == inst_data["symbol"]
        ).first()
        
        if not existing:
            instrument = Instrument(**inst_data)
            db.add(instrument)
            created += 1
            print(f"Created instrument: {inst_data['symbol']} - {inst_data['name']}")
        else:
            print(f"Instrument {inst_data['symbol']} already exists")
    
    db.commit()
    db.close()
    
    print(f"\nSeeded {created} instruments")


def main():
    """Main seeding function."""
    print("Initializing database...")
    init_db()
    
    print("\nSeeding instruments...")
    seed_instruments()
    
    print("\nSeeding complete!")


if __name__ == "__main__":
    main()

