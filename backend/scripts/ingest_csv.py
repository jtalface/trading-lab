"""Ingest historical bar data from CSV files."""
import sys
import os
import csv
from datetime import datetime, date
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Instrument, Bar
from app.engines.feature_engine import FeatureEngine


def parse_date(date_str):
    """Parse date string in various formats."""
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y%m%d", "%d-%b-%Y"]:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")


def ingest_csv(symbol: str, csv_path: str, date_col: str = "date", 
               open_col: str = "open", high_col: str = "high", 
               low_col: str = "low", close_col: str = "close",
               volume_col: str = "volume"):
    """
    Ingest bar data from CSV file.
    
    Expected CSV format:
    date,open,high,low,close,volume
    2023-01-03,4500.25,4520.50,4495.00,4510.75,1000000
    ...
    """
    db = SessionLocal()
    
    # Get instrument
    instrument = db.query(Instrument).filter(Instrument.symbol == symbol).first()
    if not instrument:
        print(f"Error: Instrument {symbol} not found. Please seed instruments first.")
        db.close()
        return
    
    print(f"Ingesting data for {instrument.name} ({symbol})...")
    
    # Read CSV
    bars_created = 0
    bars_updated = 0
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    bar_date = parse_date(row[date_col])
                    
                    # Check if bar exists
                    existing = db.query(Bar).filter(
                        Bar.instrument_id == instrument.id,
                        Bar.date == bar_date
                    ).first()
                    
                    bar_data = {
                        "open": float(row[open_col]),
                        "high": float(row[high_col]),
                        "low": float(row[low_col]),
                        "close": float(row[close_col]),
                        "volume": float(row.get(volume_col, 0))
                    }
                    
                    if existing:
                        # Update
                        for key, value in bar_data.items():
                            setattr(existing, key, value)
                        bars_updated += 1
                    else:
                        # Create new
                        bar = Bar(
                            instrument_id=instrument.id,
                            date=bar_date,
                            **bar_data
                        )
                        db.add(bar)
                        bars_created += 1
                    
                    # Commit in batches
                    if (bars_created + bars_updated) % 100 == 0:
                        db.commit()
                        print(f"  Processed {bars_created + bars_updated} bars...")
                
                except (KeyError, ValueError) as e:
                    print(f"  Warning: Skipping row due to error: {e}")
                    continue
        
        db.commit()
        print(f"\nIngested {bars_created} new bars, updated {bars_updated} existing bars")
        
        # Recompute features
        print("\nRecomputing features...")
        feature_engine = FeatureEngine()
        feature_count = feature_engine.recompute_features_for_instrument(db, instrument)
        print(f"Computed {feature_count} features")
        
    except FileNotFoundError:
        print(f"Error: File not found: {csv_path}")
    except Exception as e:
        print(f"Error during ingestion: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main ingestion function."""
    parser = argparse.ArgumentParser(description="Ingest historical bar data from CSV")
    parser.add_argument("symbol", help="Instrument symbol (e.g., ES, NQ)")
    parser.add_argument("csv_path", help="Path to CSV file")
    parser.add_argument("--date-col", default="date", help="Date column name")
    parser.add_argument("--open-col", default="open", help="Open column name")
    parser.add_argument("--high-col", default="high", help="High column name")
    parser.add_argument("--low-col", default="low", help="Low column name")
    parser.add_argument("--close-col", default="close", help="Close column name")
    parser.add_argument("--volume-col", default="volume", help="Volume column name")
    
    args = parser.parse_args()
    
    ingest_csv(
        symbol=args.symbol,
        csv_path=args.csv_path,
        date_col=args.date_col,
        open_col=args.open_col,
        high_col=args.high_col,
        low_col=args.low_col,
        close_col=args.close_col,
        volume_col=args.volume_col
    )


if __name__ == "__main__":
    main()

