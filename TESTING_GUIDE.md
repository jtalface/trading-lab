# 🧪 Testing Guide - Volatility Edge Lab

Complete guide to testing your futures trading system.

## 📋 Table of Contents

1. [Initial Setup & Verification](#initial-setup--verification)
2. [Backend API Testing](#backend-api-testing)
3. [Frontend UI Testing](#frontend-ui-testing)
4. [Unit Tests](#unit-tests)
5. [Strategy Testing](#strategy-testing)
6. [End-to-End Workflows](#end-to-end-workflows)
7. [Performance Testing](#performance-testing)

---

## 1️⃣ Initial Setup & Verification

### Step 1: Check System Status

```bash
# Check if services are running
docker-compose ps

# Should show: postgres, backend, frontend all "Up"
```

### Step 2: Initialize Database (if not done)

```bash
# Quick setup
make setup

# This runs seed, ingest, features, and demo backtest
```

### Step 3: Verify Data

```bash
# Check what's in the database
make check

# You should see:
# ✅ Instruments: 6
# ✅ ES bars: 60
# ✅ NQ bars: 60
# ✅ Features computed
```

---

## 2️⃣ Backend API Testing

### A. Health Check

```bash
# Test if backend is alive
curl http://localhost:8432/health

# Expected: {"status":"healthy"}
```

### B. Test API Endpoints

#### List Instruments
```bash
curl http://localhost:8432/instruments | jq

# Should return array of instruments with ES, NQ, etc.
```

#### Get Bars Data
```bash
# Get last 10 bars for ES (instrument_id=1)
curl http://localhost:8432/bars/1?limit=10 | jq

# Check you get OHLCV data
```

#### Get Features
```bash
# Get computed features for ES
curl http://localhost:8432/features/1?limit=10 | jq

# Should show ATR, MA, slope, HH/LL values
```

#### List Backtests
```bash
curl http://localhost:8432/backtest/runs | jq

# Should show at least the demo backtest
```

#### Get Backtest Results
```bash
# Get results for backtest ID 1
curl http://localhost:8432/backtest/1/results | jq

# Should show full results with equity curve, metrics
```

#### Test Journal
```bash
# Create a journal entry
curl -X POST http://localhost:8432/journal \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15",
    "title": "Test Entry",
    "content": "Testing the API",
    "tags": "test,api"
  }' | jq

# List journal entries
curl http://localhost:8432/journal | jq
```

### C. Interactive API Testing

Open the interactive API docs:
```bash
open http://localhost:8432/docs
```

Try each endpoint using the "Try it out" button:
- ✅ GET /instruments
- ✅ POST /bars/ingest
- ✅ POST /features/recompute-all
- ✅ POST /backtest/run
- ✅ GET /signals/today
- ✅ GET /portfolio/status

---

## 3️⃣ Frontend UI Testing

### Open the Application

```bash
open http://localhost:3847
```

### Test Each Page

#### **Home Page** (/)
- ✅ Page loads without errors
- ✅ Navigation bar shows all menu items
- ✅ Feature cards are displayed
- ✅ Strategy overview section visible
- ✅ Click on feature cards navigates to pages

#### **Strategy Lab** (/strategy-lab)

**Test 1: Load Existing Instruments**
- ✅ ES and NQ checkboxes are available
- ✅ Can select/deselect instruments
- ✅ Date pickers work
- ✅ All parameter inputs accept values

**Test 2: Run Basic Backtest**
```
1. Select: ES, NQ
2. Date range: 2023-01-03 to 2023-03-31
3. Initial Capital: $100,000
4. Leave other params as default
5. Click "Run Backtest"
6. Should redirect to Results page
```

**Test 3: Modify Parameters**
```
Try different values:
- MA Period: 20, 50, 100
- Risk per trade: 0.25%, 0.5%, 1%
- Stop ATR Multiple: 1.5, 2.0, 2.5
- Run multiple backtests to compare
```

**Test 4: Risk Parameter Changes**
```
- Set Drawdown Warning to 5%
- Set Daily Loss Limit to 1%
- Run backtest and check if risk management works
```

#### **Results Page** (/results)

**Test 1: View Demo Results**
- ✅ Select demo backtest from dropdown
- ✅ Equity curve displays correctly
- ✅ Drawdown chart shows data
- ✅ Metrics are calculated and displayed
- ✅ Configuration details are shown

**Test 2: Check Metrics**
Verify these are calculated:
- ✅ Total Return (should be % with sign)
- ✅ CAGR (annualized)
- ✅ Sharpe Ratio (ideally > 1.0)
- ✅ Sortino Ratio
- ✅ Max Drawdown (should be negative %)
- ✅ Win Rate (as percentage)
- ✅ Profit Factor (ideally > 1.0)
- ✅ Total Trades (count)

**Test 3: Chart Interactions**
- ✅ Hover over equity curve shows tooltip
- ✅ Tooltip shows date and equity value
- ✅ Drawdown chart displays negative values
- ✅ Charts are responsive (resize browser)

#### **Live Signals** (/signals)

**Test 1: View Today's Signals**
- ✅ Page loads (may show "no signals" if not live trading)
- ✅ Table headers are visible
- ✅ Filter by days works (7, 14, 30)

**Test 2: Check Signal Details**
If signals exist, verify:
- ✅ Signal type (Entry Long/Short, Exit, Stop)
- ✅ Price is shown
- ✅ Target contracts calculated
- ✅ Stop price displayed
- ✅ Reason is provided

#### **Risk Console** (/risk)

**Test 1: View Portfolio Status**
- ✅ Risk mode indicator (Normal/Warning/Halt)
- ✅ Current equity displayed
- ✅ Drawdown percentage shown
- ✅ Daily P&L visible
- ✅ Can open new trades indicator

**Test 2: Check Positions Table**
If positions exist:
- ✅ Symbol, side, contracts shown
- ✅ Entry and current prices
- ✅ Stop price displayed
- ✅ Unrealized P&L calculated

**Test 3: Equity History Chart**
- ✅ 90-day chart displays
- ✅ Line chart shows equity progression
- ✅ Tooltip works on hover

#### **Journal** (/journal)

**Test 1: Create Entry**
```
1. Click "+ New Entry"
2. Set date: today
3. Title: "First backtest successful"
4. Content: "ES strategy performed well with 5% return"
5. Tags: "ES, breakout, success"
6. Click "Save Entry"
7. Entry appears in list
```

**Test 2: Edit Entry**
```
1. Click "Edit" on any entry
2. Modify content
3. Click "Update Entry"
4. Changes are saved
```

**Test 3: Delete Entry**
```
1. Click "Delete" on an entry
2. Confirm deletion
3. Entry is removed
```

---

## 4️⃣ Unit Tests

### Run All Tests

```bash
# Run full test suite
make test

# Or:
docker-compose exec backend pytest -v

# With coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

### Test Individual Modules

```bash
# Test feature engine only
docker-compose exec backend pytest tests/test_feature_engine.py -v

# Test strategy engine only
docker-compose exec backend pytest tests/test_strategy_engine.py -v

# Test risk engine only
docker-compose exec backend pytest tests/test_risk_engine.py -v
```

### Expected Results

All tests should pass (green):
```
tests/test_feature_engine.py ✓✓✓✓✓✓✓✓
tests/test_strategy_engine.py ✓✓✓✓✓✓✓✓✓✓✓
tests/test_risk_engine.py ✓✓✓✓✓✓✓✓✓

==================== 27 passed in 2.5s ====================
```

---

## 5️⃣ Strategy Testing

### Test 1: Single Instrument Backtest

```bash
# In Strategy Lab UI:
1. Select only ES
2. Date range: 2023-01-03 to 2023-03-31
3. Initial capital: $100,000
4. Run backtest
5. Examine results
```

**What to Check:**
- ✅ Trades were executed
- ✅ Equity curve shows movement
- ✅ Max drawdown is reasonable (< 20%)
- ✅ Some trades are winners, some losers
- ✅ Position sizing is consistent

### Test 2: Multi-Instrument Portfolio

```bash
# In Strategy Lab UI:
1. Select ES + NQ
2. Same date range
3. Check if both instruments trade
4. Look for diversification benefit
```

**Compare:**
- Single ES performance
- Single NQ performance
- Combined ES+NQ performance
- Is combined Sharpe ratio higher?

### Test 3: Parameter Sensitivity

Run backtests with different MA periods:

```bash
Test A: MA(20)  - Faster, more trades
Test B: MA(50)  - Medium (default)
Test C: MA(100) - Slower, fewer trades

Compare:
- Total trades
- Win rate
- Profit factor
- Max drawdown
```

### Test 4: Risk Parameter Testing

```bash
Test A: Risk 0.25% per trade
Test B: Risk 0.50% per trade (default)
Test C: Risk 1.00% per trade

Compare:
- Total return
- Max drawdown
- Risk-adjusted returns (Sharpe)
```

### Test 5: Stop Loss Testing

```bash
Test A: 1.5 ATR stops (tighter)
Test B: 2.0 ATR stops (default)
Test C: 2.5 ATR stops (wider)

Compare:
- Win rate (tighter stops = lower win rate?)
- Profit factor
- Average winner vs. average loser
```

---

## 6️⃣ End-to-End Workflows

### Workflow 1: New Instrument

```bash
# 1. Add new instrument via API
curl -X POST http://localhost:8432/instruments \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "CL",
    "name": "Crude Oil",
    "exchange": "NYMEX",
    "tick_size": 0.01,
    "multiplier": 1000,
    "currency": "USD"
  }'

# 2. Ingest data (prepare your CSV first)
docker-compose exec backend python scripts/ingest_csv.py CL /app/data/your_data.csv

# 3. Recompute features
curl -X POST http://localhost:8432/features/recompute/3

# 4. Run backtest with new instrument
# Use Strategy Lab UI and include CL
```

### Workflow 2: Journal + Backtest

```bash
# 1. Run backtest in Strategy Lab
# 2. Note the backtest ID from Results page
# 3. Go to Journal
# 4. Create entry:
#    - Title: "Backtest #X - ES trending strategy"
#    - Link to backtest_run_id: X
#    - Document observations
# 5. Run variations
# 6. Document findings in journal
```

### Workflow 3: Complete Analysis

```bash
1. Strategy Lab: Run base case backtest
2. Results: Analyze performance, note metrics
3. Journal: Document initial observations
4. Strategy Lab: Run sensitivity tests
5. Results: Compare all backtests
6. Journal: Document conclusions
7. Signals: Check if any live signals today
8. Risk Console: Verify risk metrics
```

---

## 7️⃣ Performance Testing

### Load Testing

```bash
# Test with many backtests
for i in {1..5}; do
  curl -X POST http://localhost:8432/backtest/run \
    -H "Content-Type: application/json" \
    -d @test_backtest.json
  sleep 2
done

# Check system handles multiple backtests
```

### Data Scalability

```bash
# Test with more data
# Ingest 500+ bars per instrument
# Recompute features
# Run backtests
# Check performance
```

### Frontend Performance

```bash
# Open browser dev tools
# Network tab: Check API response times
# Performance tab: Check page load times
# Console: Check for errors or warnings
```

---

## ✅ Testing Checklist

### Before Going Live

- [ ] All unit tests pass
- [ ] Can create and view backtests
- [ ] Charts render correctly
- [ ] Journal entries save/load
- [ ] API endpoints respond < 1 second
- [ ] No console errors in browser
- [ ] Database persists after restart
- [ ] Can ingest new data
- [ ] Features compute correctly
- [ ] Risk management works as expected

### System Health

```bash
# Quick health check
curl http://localhost:8432/health
curl http://localhost:3847/api/health  # if implemented

# Check logs for errors
make logs

# Check database size
docker-compose exec postgres psql -U trader -d volatility_edge -c "
  SELECT 
    schemaname,
    tablename,
    pg_total_relation_size(schemaname||'.'||tablename) as size
  FROM pg_tables 
  WHERE schemaname = 'public'
  ORDER BY size DESC;
"
```

---

## 🐛 Troubleshooting Tests

### Tests Fail

```bash
# Check dependencies
docker-compose exec backend pip list

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend

# Check browser console for errors
```

### No Backtest Results

```bash
# Check if data exists
make check

# Look at backend logs during backtest
docker-compose logs -f backend

# Run demo backtest to verify
make demo
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
make setup
```

---

## 📊 Success Criteria

Your system is working correctly if:

1. ✅ **Demo backtest completes** with metrics
2. ✅ **Unit tests pass** (27/27)
3. ✅ **Can run custom backtests** via UI
4. ✅ **Charts display** equity curves and drawdowns
5. ✅ **Metrics calculated** (CAGR, Sharpe, etc.)
6. ✅ **Journal works** (create, edit, delete)
7. ✅ **API responds** quickly (< 1s)
8. ✅ **No errors** in logs or console

---

## 🎓 Advanced Testing

### Test Edge Cases

```python
# In Strategy Lab, test:
- Empty date range
- Very small capital ($1000)
- Very large capital ($10M)
- Single day backtest
- No instruments selected
- Extreme parameters (MA=200, Risk=10%)
```

### Test Error Handling

```bash
# Try to break things:
- Invalid instrument symbol
- Future dates for backtest
- Negative capital
- Invalid CSV format
- Duplicate journal entries
```

### Test Concurrent Users

```bash
# Open multiple browser tabs
# Run backtests simultaneously
# Check if system handles it
```

---

## 📝 Test Report Template

After testing, document your findings:

```markdown
# Test Report - Volatility Edge Lab

Date: YYYY-MM-DD
Version: 1.0

## Summary
- Tests Run: X
- Tests Passed: Y
- Tests Failed: Z

## Backend Tests
- Unit Tests: ✅ Pass
- Integration Tests: ✅ Pass
- API Endpoints: ✅ All functional

## Frontend Tests
- UI Load: ✅ Works
- Navigation: ✅ Smooth
- Charts: ✅ Display correctly
- Forms: ✅ Submit properly

## Performance
- API Response Time: Xms (avg)
- Page Load Time: Xms
- Backtest Execution: Xs per backtest

## Issues Found
1. [None / List any issues]

## Recommendations
1. [Any improvements needed]

## Sign Off
System is ready for: [Development / Staging / Production]
```

---

## 🚀 Next Steps

After testing:

1. **Document findings** in Journal
2. **Run production backtests** with real data
3. **Monitor performance** over time
4. **Iterate on strategy** based on results
5. **Deploy to production** when ready

---

**Happy Testing! 🎉**

