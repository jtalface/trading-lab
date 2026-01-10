# 📊 Data Guide - Getting Historical Data for Backtesting

Complete guide to obtaining and using data in Volatility Edge Lab.

---

## 🎯 Quick Answer

**For testing:** Use the included sample data (already in the project)
```bash
make setup  # Uses ES_sample.csv and NQ_sample.csv
```

**For real backtesting:** Download data from free or paid sources (see below)

---

## 📁 Included Sample Data

### What's Included
```
/data/sample_data/
├── ES_sample.csv  (60 days, Q1 2023)
└── NQ_sample.csv  (60 days, Q1 2023)
```

### How to Use Sample Data
```bash
# Option 1: Automatic setup (recommended)
make setup

# Option 2: Manual steps
make seed    # Create instruments
make ingest  # Load ES + NQ data
make check   # Verify data loaded
make demo    # Run backtest
```

---

## 🌐 Free Data Sources

### 1. Yahoo Finance (Easiest)

**Pros:** Free, easy, no API key needed  
**Cons:** Index data only (not actual futures), limited history

**Method 1: Use Our Script**
```bash
# Install yfinance
docker-compose exec backend pip install yfinance

# Download data (last 2 years)
docker-compose exec backend python scripts/download_yahoo_data.py

# Ingest downloaded data
docker-compose exec backend python scripts/ingest_csv.py ES /app/data/sample_data/ES_yahoo.csv
```

**Method 2: Python Script**
```python
import yfinance as yf

# Download S&P 500 data (proxy for ES)
df = yf.download('^GSPC', start='2022-01-01', end='2024-01-01')
df.to_csv('ES_data.csv')

# Download NASDAQ data (proxy for NQ)
df = yf.download('^IXIC', start='2022-01-01', end='2024-01-01')
df.to_csv('NQ_data.csv')
```

**What you get:**
- ES → ^GSPC (S&P 500 Index)
- NQ → ^IXIC (NASDAQ Composite)
- YM → ^DJI (Dow Jones)
- RTY → ^RUT (Russell 2000)
- CL → CL=F (Crude Oil Futures)
- GC → GC=F (Gold Futures)

---

### 2. Alpha Vantage

**Pros:** Free API, good documentation  
**Cons:** Rate limited (5 calls/min, 500/day)

**Setup:**
1. Get free API key: https://www.alphavantage.co/support/#api-key
2. Download data:

```bash
# Example: Download SPY (S&P 500 ETF as ES proxy)
curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SPY&apikey=YOUR_KEY&outputsize=full&datatype=csv" > ES_data.csv

# Example: Download QQQ (NASDAQ ETF as NQ proxy)
curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=QQQ&apikey=YOUR_KEY&outputsize=full&datatype=csv" > NQ_data.csv
```

---

### 3. TradingView (Manual Export)

**Pros:** Free, visual charts, actual futures data  
**Cons:** Manual process, limited export on free tier

**Steps:**
1. Go to https://www.tradingview.com/
2. Search for: `ES1!` (E-mini S&P 500 continuous)
3. Set timeframe to Daily
4. Click "..." → "Export chart data"
5. Save CSV file
6. Rename columns to match format
7. Ingest into system

---

### 4. Quandl / Nasdaq Data Link

**Pros:** Structured financial data, good API  
**Cons:** Limited free data, futures data often premium

**Setup:**
```bash
pip install quandl

# Get API key from: https://data.nasdaq.com/sign-up
# Then:
import quandl
quandl.ApiConfig.api_key = "YOUR_KEY"
df = quandl.get("CHRIS/CME_ES1")  # ES continuous contract
```

---

### 5. QuantConnect / QuantLib

**Pros:** Free data for backtesting, large datasets  
**Cons:** Need account, more complex setup

- Website: https://www.quantconnect.com/
- Free tier includes futures data
- Can download via their platform

---

## 💼 Professional Data Sources (Paid)

### For Serious Trading

| Source | Cost | Data Quality | API | Notes |
|--------|------|--------------|-----|-------|
| **Interactive Brokers** | Account req'd | Excellent | Yes | Best if you trade with them |
| **CQG** | $$$$ | Professional | Yes | Industry standard |
| **Databento** | Pay-as-you-go | Excellent | Yes | Developer-friendly |
| **Polygon.io** | $199-999/mo | Very good | Yes | Good pricing |
| **NinjaTrader** | Free w/ account | Good | Yes | Free with broker account |
| **TradeStation** | Account req'd | Good | Yes | Free with account |
| **TD Ameritrade** | Free w/ account | Good | Yes | Via thinkorswim |

---

## 📋 Data Format Requirements

### Required CSV Format

```csv
date,open,high,low,close,volume
2023-01-03,4500.25,4520.50,4495.00,4510.75,2500000
2023-01-04,4510.75,4530.00,4505.00,4525.25,2400000
2023-01-05,4525.25,4540.50,4520.00,4535.00,2300000
```

### Column Requirements

| Column | Required | Format | Notes |
|--------|----------|--------|-------|
| `date` | ✅ Yes | YYYY-MM-DD | Also accepts MM/DD/YYYY, YYYYMMDD |
| `open` | ✅ Yes | Float | Opening price |
| `high` | ✅ Yes | Float | Highest price |
| `low` | ✅ Yes | Float | Lowest price |
| `close` | ✅ Yes | Float | Closing price |
| `volume` | ⚠️ Optional | Integer | Can be 0 if unavailable |

### Data Quality Requirements

- **Minimum bars:** 60+ (for MA(50) + buffer)
- **Recommended:** 250+ bars (1 year daily data)
- **Ideal:** 500-1000+ bars (2-4 years)
- **No gaps:** Fill missing days or system will skip them
- **Chronological:** Oldest to newest (system will handle either way)
- **Adjusted:** Use adjusted prices if possible

---

## 🔧 Converting Your Data

### If You Have Different Column Names

```bash
# Use ingest script with custom columns
docker-compose exec backend python scripts/ingest_csv.py ES /app/data/your_data.csv \
  --date-col "Date" \
  --open-col "Open" \
  --high-col "High" \
  --low-col "Low" \
  --close-col "Close" \
  --volume-col "Vol"
```

### If You Have Excel File

```python
import pandas as pd

# Read Excel
df = pd.read_excel('data.xlsx')

# Rename columns
df = df.rename(columns={
    'Date': 'date',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume'
})

# Save as CSV
df.to_csv('data.csv', index=False)
```

### If You Have JSON/Other Format

```python
import pandas as pd
import json

# Read JSON
with open('data.json') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Format and save
df.to_csv('data.csv', index=False)
```

---

## 📥 Complete Workflow

### Step-by-Step: From Download to Backtest

**1. Download Data**
```bash
# Using Yahoo Finance (example)
docker-compose exec backend pip install yfinance
docker-compose exec backend python scripts/download_yahoo_data.py
```

**2. Verify File Format**
```bash
# Check first few lines
head /Users/alface/Repos/Tutorials/AI/trader/data/sample_data/ES_yahoo.csv
```

**3. Ingest Data**
```bash
# Ingest ES data
docker-compose exec backend python scripts/ingest_csv.py ES /app/data/sample_data/ES_yahoo.csv

# Ingest NQ data
docker-compose exec backend python scripts/ingest_csv.py NQ /app/data/sample_data/NQ_yahoo.csv
```

**4. Verify Data Loaded**
```bash
# Check what's in database
make check

# Should show:
# ✅ ES: 500+ bars
# ✅ NQ: 500+ bars
# ✅ Features computed
```

**5. Run Backtest**
```bash
# Via command line
make demo

# Or via UI
open http://localhost:3847
# Navigate to Strategy Lab
```

---

## 💡 Data Tips & Best Practices

### Amount of Data Needed

| Purpose | Minimum Bars | Recommended | Ideal |
|---------|--------------|-------------|-------|
| Testing system | 60 | 100 | 250+ |
| Strategy development | 250 | 500 | 1000+ |
| Robust backtesting | 500 | 1000 | 2500+ |
| Statistical significance | 1000 | 2000+ | 5000+ |

### Data Quality Checklist

- [ ] No missing dates (or gaps are intentional)
- [ ] No zero/null values in OHLC
- [ ] High ≥ Low, High ≥ Open, High ≥ Close
- [ ] Low ≤ Open, Low ≤ Close
- [ ] Reasonable price movements (no 1000% jumps)
- [ ] Consistent date format
- [ ] At least 60 bars for MA(50)

### Common Issues & Solutions

**Issue: "Not enough data for MA(50)"**
```
Solution: Download more historical data (need 60+ bars)
```

**Issue: "Date format not recognized"**
```
Solution: Convert dates to YYYY-MM-DD format
Or use --date-col parameter with your format
```

**Issue: "No data available for backtest"**
```
Solution: Check with `make check`
Verify data was ingested successfully
```

**Issue: "Features not computed"**
```
Solution: Features auto-compute during ingest
If missing, run: curl -X POST http://localhost:8432/features/recompute-all
```

---

## 🎯 Quick Start Options

### Option 1: Use Sample Data (Fastest)
```bash
make setup  # Done in 1 minute!
```

### Option 2: Download 2 Years from Yahoo
```bash
docker-compose exec backend pip install yfinance
docker-compose exec backend python scripts/download_yahoo_data.py
docker-compose exec backend python scripts/ingest_csv.py ES /app/data/sample_data/ES_yahoo.csv
docker-compose exec backend python scripts/ingest_csv.py NQ /app/data/sample_data/NQ_yahoo.csv
make demo
```

### Option 3: Use Your Own Data
```bash
# 1. Copy your CSV to data folder
cp ~/Downloads/my_data.csv /Users/alface/Repos/Tutorials/AI/trader/data/sample_data/

# 2. Ingest it
docker-compose exec backend python scripts/ingest_csv.py ES /app/data/sample_data/my_data.csv

# 3. Check it loaded
make check

# 4. Run backtest
open http://localhost:3847
```

---

## 📚 Additional Resources

### Data Documentation
- **Yahoo Finance API:** https://pypi.org/project/yfinance/
- **Alpha Vantage Docs:** https://www.alphavantage.co/documentation/
- **Quandl Docs:** https://docs.data.nasdaq.com/

### Futures Symbols Reference
- **CME Group:** https://www.cmegroup.com/
- **TradingView:** https://www.tradingview.com/markets/futures/

### Where to Learn More
- `README.md` - System overview
- `README-ACRONYMS.md` - Trading terms
- `TRADER_GUIDE.md` - How to use the system
- `TESTING_GUIDE.md` - How to test

---

## ⚠️ Important Notes

### About Sample Data
- ✅ Good for: Testing system, learning, demos
- ❌ Not good for: Real trading decisions, strategy validation
- Note: Only 60 days, Q1 2023 data

### About Yahoo Finance Data
- ✅ Good for: Learning, development, rough backtests
- ❌ Not good for: Professional trading (uses indexes, not actual futures)
- Note: Free but not tick-accurate futures data

### About Professional Data
- ✅ Good for: Serious backtesting, live trading
- ❌ Not good for: Beginners (expensive, complex)
- Note: Worth it if trading with real money

### Data Disclaimer
⚠️ **Historical data does not guarantee future results.**  
⚠️ **Backtest results can be misleading.**  
⚠️ **Always use out-of-sample testing.**  
⚠️ **Start small with real money.**

---

## 🆘 Need Help?

```bash
# Check what data you have
make check

# View logs
make logs

# Check documentation
cat DATA_GUIDE.md
cat TRADER_GUIDE.md
cat README-ACRONYMS.md
```

---

**Ready to get data? Start with:** `make setup` 🚀

