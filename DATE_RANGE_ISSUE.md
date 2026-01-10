# 🔍 Date Range Issue - SOLVED

## What Was Wrong

You were getting this error:
```
Backtest failed: No data available for selected instruments and date range
```

Even though you selected the correct dates (2023-01-03 to 2023-03-31) that match your sample data.

## Root Cause

The issue is that **features require a warmup period** before they can be calculated.

### Here's What Happened:

1. ✅ **Bar Data**: You have 62 days of OHLCV data from 2023-01-03 to 2023-03-31
2. ⏳ **Feature Calculation**: The strategy uses MA(50), which needs 50 days of historical bars
3. ❌ **Features Available**: Features only start appearing from day 50+ onwards (2023-03-15)

### Visual Explanation:

```
Jan 3                    Mar 15              Mar 31
|------------------------|-------------------|
    Warmup Period          Features Available
    (50 days)              (13 days)
    
Bar Data:  [============================================]  62 bars
Features:                 [=====================]         13 features
                          ↑
                    First feature appears here
                    after 50-day warmup
```

## ✅ Solution

### Quick Fix: Use the Correct Date Range

Run this command to see what dates are actually available:

```bash
make dates
```

Output:
```
📊 ES - E-mini S&P 500
  Bar Data:     2023-01-03 to 2023-03-31 (62 bars)
  Feature Data: 2023-03-15 to 2023-03-31 (13 features)
  
  ✅ BACKTEST RANGE: 2023-03-15 to 2023-03-31
     Use these dates in Strategy Lab for ES
```

### In the UI:

1. Go to Strategy Lab (http://localhost:3847)
2. Select ES and/or NQ
3. **Set Start Date: 2023-03-15** (not Jan 3!)
4. Set End Date: 2023-03-31
5. Click "Run Backtest"
6. ✅ It will work!

## 📈 To Backtest From January

If you want to backtest from January 3rd, you need bar data starting **at least 50 days earlier**.

### Calculate Required Start Date:

```
Desired backtest start: 2023-01-03
MA(50) warmup needed:   50 trading days
Data should start:      ~2022-11-01 (or earlier)
```

### Steps:

1. **Download more historical data** (see `DATA_GUIDE.md`)
   - Use Yahoo Finance, Alpha Vantage, or other sources
   - Get data from Nov 2022 to March 2023 (or longer)

2. **Ingest the data**:
   ```bash
   docker-compose exec backend python scripts/ingest_csv.py data/your_data.csv ES
   ```

3. **Recompute features**:
   ```bash
   curl -X POST http://localhost:8432/features/recompute-all
   ```

4. **Check new date range**:
   ```bash
   make dates
   ```

5. **Now you can backtest from Jan 3rd!** ✅

## 🎯 Key Takeaway

**Always run `make dates` before backtesting** to see what date ranges are actually available.

The date range depends on:
- How much bar data you have
- The longest lookback period in your strategy (MA50 = 50 days)
- Features can only be calculated after the warmup period

## 📚 More Help

- **Troubleshooting**: See `TROUBLESHOOTING.md`
- **Data Sources**: See `DATA_GUIDE.md`
- **Quick Start**: See `QUICKSTART.md`

## 🛠️ Useful Commands

```bash
# Check available backtest dates
make dates

# Check database status
make check

# Run demo backtest (uses correct dates automatically)
make demo

# View backend logs
docker-compose logs backend --tail=50
```

---

**You're all set! Just use 2023-03-15 to 2023-03-31 and it will work.** 🎉

