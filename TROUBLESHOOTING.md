# Troubleshooting Guide

## Common Issues and Solutions

### ❌ "No data available for selected instruments and date range"

**Symptom**: Backtest fails immediately with this error message.

**Cause**: The date range you selected doesn't have computed features available.

**Why This Happens**:
- Features require historical bar data for calculation
- MA(50) needs 50 days of historical bars
- ATR(20) needs 20 days of historical bars
- The first features only appear after the **warmup period** (50+ days)

**Example**:
```
Bar Data:     2023-01-03 to 2023-03-31 (62 bars)
Feature Data: 2023-03-15 to 2023-03-31 (13 features)
Warmup:       71 days
```

If you have 62 days of bars starting Jan 3rd, features only become available from day 50+ onwards (around March 15th).

**Solutions**:

#### Solution 1: Use Available Date Range (Quick Fix)
```bash
# Check what dates are actually available
make dates
```

This will show you the exact date ranges you can use for backtesting:
```
✅ BACKTEST RANGE: 2023-03-15 to 2023-03-31
   Use these dates in Strategy Lab for ES
```

Then in the UI:
1. Go to Strategy Lab (http://localhost:3847)
2. Set **Start Date**: `2023-03-15`
3. Set **End Date**: `2023-03-31`
4. Run backtest ✅

#### Solution 2: Add More Historical Data (Better)
To backtest from January 3rd, you need bar data starting **at least 50 days earlier**.

**Calculate Required Start Date**:
```
Desired backtest start: 2023-01-03
Warmup period needed:   50 days (for MA50)
Data should start from: ~2022-11-01 (or earlier)
```

**Steps**:
1. Download more historical data (see `DATA_GUIDE.md`)
2. Ingest the data:
   ```bash
   docker-compose exec backend python scripts/ingest_csv.py data/sample_data/ES_extended.csv ES
   ```
3. Recompute features:
   ```bash
   curl -X POST http://localhost:8432/features/recompute-all
   ```
4. Check new date range:
   ```bash
   make dates
   ```

---

### ❌ "No active instruments found"

**Symptom**: Backtest fails with "No active instruments found for symbols: ['ES', 'NQ']"

**Cause**: Instruments haven't been seeded in the database.

**Solution**:
```bash
make setup
```

Or manually:
```bash
docker-compose exec backend python scripts/seed_data.py
```

---

### ❌ Features Not Computed

**Symptom**: `make dates` shows "❌ No features computed"

**Cause**: Features haven't been calculated yet.

**Solution**:
```bash
# Via API
curl -X POST http://localhost:8432/features/recompute-all

# Or via make
make setup
```

---

### ❌ Port Already in Use

**Symptom**: 
```
Error: bind: address already in use
```

**Cause**: Another process is using ports 3847 (frontend) or 8432 (backend).

**Solution**:

Check what's using the ports:
```bash
# Check frontend port
lsof -i :3847

# Check backend port
lsof -i :8432
```

Kill the process:
```bash
kill -9 <PID>
```

Or change ports in:
- `docker-compose.yml`
- `frontend/next.config.js`
- `frontend/lib/api.ts`
- `backend/Dockerfile`

---

### ❌ Database Connection Error

**Symptom**: Backend logs show "could not connect to server"

**Cause**: PostgreSQL container isn't running or isn't ready.

**Solution**:
```bash
# Check container status
docker-compose ps

# Restart database
docker-compose restart db

# Wait for it to be ready (10-15 seconds)
sleep 15

# Restart backend
docker-compose restart backend
```

---

### ❌ Frontend Can't Connect to Backend

**Symptom**: Frontend shows network errors or "Failed to fetch"

**Cause**: Backend isn't running or wrong API URL.

**Check**:
1. Backend is running:
   ```bash
   docker-compose ps backend
   ```

2. Backend is accessible:
   ```bash
   curl http://localhost:8432/instruments
   ```

3. Frontend has correct API URL:
   ```bash
   # Check frontend/next.config.js
   grep API_BASE_URL frontend/next.config.js
   # Should show: http://localhost:8432
   ```

**Solution**:
```bash
# Restart services
docker-compose restart backend frontend

# Or rebuild if needed
docker-compose up --build -d
```

---

### ❌ Backtest Runs Forever (Status: "running")

**Symptom**: Backtest status stays "running" and never completes.

**Cause**: Background task crashed or is stuck.

**Check Backend Logs**:
```bash
docker-compose logs backend | tail -50
```

Look for errors or exceptions.

**Solution**:
```bash
# Restart backend to clear stuck tasks
docker-compose restart backend

# Try backtest again with a smaller date range
# e.g., 2023-03-15 to 2023-03-20 (5 days)
```

---

### ❌ Empty Charts / No Results

**Symptom**: Backtest completes but charts are empty.

**Cause**: Not enough data in the selected range, or no trades were generated.

**Check**:
1. Date range has enough data:
   ```bash
   make dates
   ```

2. Backtest results:
   - Go to Results page
   - Check "Total Trades" - if 0, strategy didn't generate any signals
   - Check error message if any

**Solution**:
- Use a longer date range (more days = more opportunity for trades)
- Adjust strategy parameters (e.g., shorter MA period, wider breakout period)
- Check if market conditions in your data range match strategy filters

---

## Quick Diagnostic Commands

```bash
# Check everything is running
docker-compose ps

# Check database has data
make check

# Check available backtest dates
make dates

# View backend logs
docker-compose logs backend --tail=50

# View frontend logs
docker-compose logs frontend --tail=50

# Restart everything
docker-compose restart

# Full reset (nuclear option - deletes all data!)
docker-compose down -v
make setup
```

---

## Getting Help

If you're still stuck:

1. **Check the logs**:
   ```bash
   docker-compose logs backend | grep -i error
   docker-compose logs frontend | grep -i error
   ```

2. **Verify your setup**:
   ```bash
   make check
   make dates
   ```

3. **Try the demo**:
   ```bash
   make demo
   ```
   If the demo works, your issue is likely with date ranges or data.

4. **Check the guides**:
   - `README.md` - Full documentation
   - `QUICKSTART.md` - Setup instructions
   - `TESTING_GUIDE.md` - Testing procedures
   - `DATA_GUIDE.md` - Data sources and ingestion
   - `TRADER_GUIDE.md` - How to use the app

---

## Prevention Tips

✅ **Always check available dates before running a backtest**:
```bash
make dates
```

✅ **Use the correct date range** shown by `make dates`

✅ **Ensure data is loaded** before backtesting:
```bash
make check
# Should show instruments, bars, and features
```

✅ **Start with the demo** to verify everything works:
```bash
make demo
```

✅ **Use smaller date ranges** for testing (faster, easier to debug)

✅ **Check logs** if something goes wrong:
```bash
docker-compose logs backend --tail=100
```

