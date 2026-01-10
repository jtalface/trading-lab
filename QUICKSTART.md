# 🚀 Quick Start Guide

Get up and running with Volatility Edge Lab in 5 minutes!

## Prerequisites

✅ Docker and Docker Compose installed  
✅ 8GB RAM available  
✅ Ports 3847, 5432, and 8432 free  

## Step-by-Step Setup

### 1. Clone and Start Services (2 min)

```bash
# Clone the repository
git clone <your-repo-url>
cd trader

# Start all services
docker-compose up -d

# Wait for services to be ready (check with)
docker-compose ps
```

### 2. Complete Setup - All-in-One (2 min)

```bash
# This single command does everything:
# - Seeds instruments
# - Ingests ES & NQ data
# - Verifies setup
make setup

# Or manually:
docker-compose exec backend python scripts/setup_complete.py
```

**Alternative: Step-by-Step Setup**

If you prefer to run each step separately:

```bash
# Check current status
make check

# Seed instruments (ES, NQ, YM, RTY, CL, GC)
make seed

# Load sample data
make ingest

# Verify everything is ready
make check
```

### 3. Run Demo Backtest (1 min)

```bash
make demo

# Or:
docker-compose exec backend python scripts/run_demo_backtest.py
```

You should see output like:
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
...
```

### 4. Access the UI

Open your browser and navigate to:

- **Frontend**: http://localhost:3847
- **API Docs**: http://localhost:8432/docs

## First Actions in UI

### Strategy Lab
1. Navigate to "Strategy Lab"
2. Select ES and NQ instruments
3. Set date range (2023-01-03 to 2023-03-31)
4. Click "Run Backtest"
5. Wait ~10 seconds for completion

### Results Page
1. Navigate to "Results"
2. Select your backtest from dropdown
3. View equity curve and metrics
4. Analyze drawdown chart

### Live Signals
1. Navigate to "Live Signals"
2. View today's signals (if any)
3. Check recent signal history

### Risk Console
1. Navigate to "Risk Console"
2. View portfolio metrics
3. Check current positions
4. Monitor risk status

### Journal
1. Navigate to "Journal"
2. Click "+ New Entry"
3. Document your observations
4. Add tags for organization

## Common Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart backend
docker-compose restart frontend

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v

# Access backend shell
docker-compose exec backend bash

# Run tests
docker-compose exec backend pytest

# Recompute all features
curl -X POST http://localhost:8432/features/recompute-all
```

## Troubleshooting

### Services won't start
```bash
# Check ports are free
lsof -i :3847
lsof -i :8432
lsof -i :5432

# Kill conflicting processes or change ports in docker-compose.yml
```

### Database connection errors
```bash
# Check postgres is running
docker-compose ps postgres

# View postgres logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Frontend can't reach backend
```bash
# Check backend is healthy
curl http://localhost:8432/health

# Should return: {"status":"healthy"}
```

### Backtests fail
```bash
# Check you've seeded data
docker-compose exec backend python -c "from app.database import SessionLocal; from app.models import Instrument; db = SessionLocal(); print(f'Instruments: {db.query(Instrument).count()}')"

# Should show at least 2-6 instruments

# Check you've loaded bars
docker-compose exec backend python -c "from app.database import SessionLocal; from app.models import Bar; db = SessionLocal(); print(f'Bars: {db.query(Bar).count()}')"

# Should show 100+ bars
```

## Next Steps

1. **Load Your Own Data**
   ```bash
   # Prepare CSV in format: date,open,high,low,close,volume
   docker-compose exec backend python scripts/ingest_csv.py SYMBOL /app/data/your_data.csv
   ```

2. **Customize Strategy**
   - Adjust MA periods (20, 50, 100, 200)
   - Change breakout windows (10, 20, 40)
   - Tune ATR stop multiples (1.5, 2.0, 2.5)
   - Modify risk per trade (0.25%, 0.5%, 1%)

3. **Add More Instruments**
   - Use API to add instruments
   - Or modify `scripts/seed_data.py`
   - Ingest historical data
   - Run multi-instrument backtests

4. **Optimize Parameters**
   - Run multiple backtests
   - Compare performance metrics
   - Document in journal
   - Iterate and improve

## API Quick Reference

```bash
# List instruments
curl http://localhost:8432/instruments

# Get bars for ES (instrument_id=1)
curl http://localhost:8432/bars/1?limit=10

# List backtests
curl http://localhost:8432/backtest/runs

# Get backtest results
curl http://localhost:8432/backtest/1/results

# Create journal entry
curl -X POST http://localhost:8432/journal \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-15",
    "title": "First Trade",
    "content": "Learned about breakout entries today..."
  }'
```

## Development Mode

### Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export USE_SQLITE=true
uvicorn app.main:app --reload
```

### Frontend (Node)
```bash
cd frontend
npm install
npm run dev
```

## Support

- 📖 Full documentation: See [README.md](README.md)
- 🐛 Issues: Open on GitHub
- 💬 Questions: Check API docs at http://localhost:8432/docs

## Port Reference

- **Frontend UI**: http://localhost:3847
- **Backend API**: http://localhost:8432
- **PostgreSQL**: localhost:5432

---

**You're all set! Happy trading! 🎉**

