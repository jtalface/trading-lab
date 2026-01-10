# Backend Scripts

Utility scripts for data management and system operations.

## Scripts Overview

### 1. seed_data.py

Seeds the database with initial instrument definitions.

**Usage:**
```bash
python scripts/seed_data.py
```

**What it does:**
- Creates common futures instruments (ES, NQ, YM, RTY, CL, GC)
- Sets up tick sizes and multipliers
- Configures exchange and currency information

**Run this first** before ingesting any bar data.

### 2. ingest_csv.py

Ingests historical OHLCV bar data from CSV files.

**Usage:**
```bash
python scripts/ingest_csv.py <SYMBOL> <CSV_PATH> [options]
```

**Arguments:**
- `SYMBOL`: Instrument symbol (e.g., ES, NQ)
- `CSV_PATH`: Path to CSV file containing bar data

**Options:**
- `--date-col`: Column name for date (default: "date")
- `--open-col`: Column name for open (default: "open")
- `--high-col`: Column name for high (default: "high")
- `--low-col`: Column name for low (default: "low")
- `--close-col`: Column name for close (default: "close")
- `--volume-col`: Column name for volume (default: "volume")

**CSV Format:**
```csv
date,open,high,low,close,volume
2023-01-03,3850.50,3900.25,3840.00,3895.75,2500000
2023-01-04,3895.75,3920.50,3880.00,3910.25,2400000
```

**Supported date formats:**
- `YYYY-MM-DD` (e.g., 2023-01-03)
- `MM/DD/YYYY` (e.g., 01/03/2023)
- `YYYYMMDD` (e.g., 20230103)
- `DD-Mon-YYYY` (e.g., 03-Jan-2023)

**Examples:**
```bash
# Basic usage
python scripts/ingest_csv.py ES data/ES_daily.csv

# Custom column names
python scripts/ingest_csv.py NQ data/nasdaq.csv --date-col Date --close-col Close

# Full path example
python scripts/ingest_csv.py CL /app/data/sample_data/CL_sample.csv
```

**What it does:**
1. Validates instrument exists in database
2. Reads CSV file row by row
3. Creates or updates bar records
4. Commits in batches (every 100 bars)
5. Automatically recomputes technical features

### 3. run_demo_backtest.py

Runs a demonstration backtest using sample data.

**Usage:**
```bash
python scripts/run_demo_backtest.py
```

**What it does:**
- Creates a backtest on ES and NQ
- Uses Q1 2023 data (Jan-Mar)
- Runs with default strategy parameters
- Displays performance metrics
- Stores results in database

**Output:**
```
============================================================
BACKTEST RESULTS
============================================================
Status: completed
Initial Capital: $100,000.00
Final Equity: $105,234.50
Total Return: 5.23%
CAGR: 22.45%
Sharpe Ratio: 1.85
Sortino Ratio: 2.41
Max Drawdown: 8.32%
Max DD Duration: 12 days
Total Trades: 15
Win Rate: 60.00%
Profit Factor: 1.85
============================================================
```

## Workflow Examples

### Complete Setup from Scratch

```bash
# 1. Seed instruments
python scripts/seed_data.py

# 2. Ingest data for ES
python scripts/ingest_csv.py ES ../data/sample_data/ES_sample.csv

# 3. Ingest data for NQ
python scripts/ingest_csv.py NQ ../data/sample_data/NQ_sample.csv

# 4. Run demo backtest
python scripts/run_demo_backtest.py
```

### Adding New Data

```bash
# Download new data (external process)
# Then ingest it
python scripts/ingest_csv.py ES data/ES_2024.csv

# Features are automatically recomputed
# Ready for backtesting!
```

### Updating Existing Data

The ingest script automatically handles updates:
- If a bar for a date already exists, it updates it
- If a bar doesn't exist, it creates it
- Useful for corrections or filling gaps

## Using Docker

When running in Docker, prefix commands with `docker-compose exec backend`:

```bash
# Seed data
docker-compose exec backend python scripts/seed_data.py

# Ingest CSV
docker-compose exec backend python scripts/ingest_csv.py ES /app/data/sample_data/ES_sample.csv

# Run demo
docker-compose exec backend python scripts/run_demo_backtest.py
```

Note the `/app` prefix for file paths - this is the working directory inside the container.

## Troubleshooting

### "Instrument not found"
Make sure you've run `seed_data.py` first, or create the instrument via API.

### "File not found"
Check your file path. In Docker, remember to use `/app` prefix and ensure the file is in a mounted volume.

### "Unable to parse date"
Verify your CSV date format. The script supports common formats but you may need to specify column names.

### Features not computing
Ensure you have enough data bars:
- MA(50) requires at least 50 bars
- HH/LL(20) requires at least 20 bars
- First ~50 bars may not have all features

### Database errors
- Check database connection in `.env`
- Ensure database is running
- Verify permissions

## Advanced Usage

### Programmatic Usage

You can also use these scripts programmatically:

```python
from scripts.ingest_csv import ingest_csv
from scripts.seed_data import seed_instruments

# Seed instruments
seed_instruments()

# Ingest data
ingest_csv(
    symbol='ES',
    csv_path='data/ES_daily.csv',
    date_col='Date',
    close_col='Close'
)
```

### Batch Processing

Process multiple files:

```bash
#!/bin/bash
for file in data/*.csv; do
    symbol=$(basename $file .csv)
    python scripts/ingest_csv.py $symbol $file
done
```

### Custom Instruments

To add a custom instrument, either:

1. Use the API:
```bash
curl -X POST http://localhost:8432/instruments \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "ZB",
    "name": "30-Year T-Bond",
    "exchange": "CBOT",
    "tick_size": 0.03125,
    "multiplier": 1000,
    "currency": "USD"
  }'
```

2. Modify `seed_data.py` to include your instrument.

## Data Requirements

For proper backtesting, ensure your data:
- Has at least 60+ bars (for MA(50) + lookback)
- Is sorted chronologically
- Has no gaps in critical periods
- Includes all required OHLCV columns
- Uses consistent date format

## Performance Tips

- Ingest commits every 100 rows (adjust if needed)
- Feature computation happens after ingestion
- Large files (>1000 bars) may take 1-2 minutes
- Consider using PostgreSQL for better performance with large datasets

