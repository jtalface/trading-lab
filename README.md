# Volatility Edge Lab – Futures Trend v1

A production-quality futures trend-following trading system with volatility-based position sizing, comprehensive risk management, and robust backtesting capabilities.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)

## 🎯 Overview

This system implements a professional-grade futures trend-following strategy with:

- **Breakout Entry Logic**: Enter trends based on 20-day high/low breakouts
- **Volatility-Based Stops**: Dynamic stop placement using ATR (Average True Range)
- **Intelligent Position Sizing**: Risk 0.5% per trade with automatic contract calculation
- **Robust Risk Management**: Multi-layered guardrails including drawdown limits and daily loss caps
- **Event-Driven Backtesting**: Realistic simulation with slippage, commissions, and proper fill execution
- **Modern UI**: Clean, responsive interface for strategy configuration and results analysis

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Strategy Details](#strategy-details)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### Core Strategy Engine

- **Trend Filter**: MA(50) with slope confirmation ensures you're trading with the trend
- **Breakout Entry**: 20-day high/low breakouts for precise timing
- **Dynamic Exits**: 10-day high/low crosses for profit-taking
- **Catastrophe Stops**: 2× ATR stops always enforced using intraday high/low
- **Cooldown Period**: 3-day waiting period after exits prevents over-trading

### Risk Management

- **Position Sizing**: Automatic contract calculation based on stop distance and equity risk
- **Exposure Limits**: Maximum contracts per instrument and total portfolio exposure caps
- **Correlation Management**: Special handling for correlated instruments (ES+NQ)
- **Drawdown Guardrails**:
  - 10% drawdown → halve position sizes
  - 15% drawdown → stop all new entries
  - 2% daily loss → trading halt for the day

### Backtesting System

- **Event-Driven**: Processes daily bars sequentially for realistic simulation
- **Realistic Execution**: Next-day open entries with configurable slippage and commissions
- **Comprehensive Metrics**: CAGR, Sharpe, Sortino, max drawdown, win rate, profit factor
- **Detailed Tracking**: Full trade history, position snapshots, and signal logs

### User Interface

- **Strategy Lab**: Configure and launch backtests with intuitive parameter controls
- **Results Dashboard**: Interactive equity curves, drawdown charts, and performance metrics
- **Live Signals**: Monitor entry/exit signals with position sizing and stop levels
- **Risk Console**: Real-time portfolio metrics and risk status
- **Trading Journal**: Document observations and track learning

## 🛠 Tech Stack

### Backend
- **Python 3.11**: Core application language
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: Robust ORM for database operations
- **PostgreSQL/SQLite**: Production and local database options
- **pandas/numpy**: Quantitative analysis and feature computation

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Modern, utility-first styling
- **Recharts**: Beautiful, responsive charts
- **SWR**: Data fetching and caching

### Infrastructure
- **Docker Compose**: Containerized development environment
- **pytest**: Comprehensive test suite
- **Alembic**: Database migrations

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git installed
- 8GB RAM minimum (for running all services)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trader
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database (port 5432)
   - Backend API (port 8000)
   - Frontend UI (port 3000)

3. **Seed the database with sample instruments**
   ```bash
   docker-compose exec backend python scripts/seed_data.py
   ```

4. **Ingest sample data**
   ```bash
   docker-compose exec backend python scripts/ingest_csv.py ES /app/data/sample_data/ES_sample.csv
   docker-compose exec backend python scripts/ingest_csv.py NQ /app/data/sample_data/NQ_sample.csv
   ```

5. **Run a demo backtest**
   ```bash
   docker-compose exec backend python scripts/run_demo_backtest.py
   ```

6. **Access the application**
   - Frontend: http://localhost:3847
   - API Docs: http://localhost:8432/docs
   - API Health: http://localhost:8432/health

### Alternative: Local Development (Without Docker)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment for SQLite
export USE_SQLITE=true

# Seed data and run
python scripts/seed_data.py
python scripts/ingest_csv.py ES ../data/sample_data/ES_sample.csv
python scripts/ingest_csv.py NQ ../data/sample_data/NQ_sample.csv

# Start the backend
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

## 📊 Strategy Details

### Entry Rules

1. **Trend Filter (Must Pass)**
   - Long: Close > MA(50) AND MA(50) slope > 0
   - Short: Close < MA(50) AND MA(50) slope < 0

2. **Breakout Trigger**
   - Long: Close breaks above 20-day high
   - Short: Close breaks below 20-day low

3. **Execution**
   - Enter at next day's open price
   - Apply slippage (default: 1 tick)
   - Place stop at entry ± 2× ATR(20)

### Exit Rules

1. **Profit Target Exit**
   - Long: Close crosses below 10-day low
   - Short: Close crosses above 10-day high

2. **Stop Loss**
   - Catastrophe stop always active
   - Checked using intraday high/low
   - Long: Exits if low ≤ stop
   - Short: Exits if high ≥ stop

3. **Cooldown Period**
   - After any exit, wait 3 trading days
   - Prevents re-entry same direction
   - Exception: New 20-day breakout overrides cooldown

### Position Sizing

Formula: `Contracts = floor(RiskAmount / StopDistance)`

Where:
- `RiskAmount = Equity × RiskPerTrade × RiskMultiplier`
- `StopDistance = |EntryPrice - StopPrice| × ContractMultiplier`
- `RiskMultiplier`:
  - 1.0 (normal mode)
  - 0.5 (warning mode, drawdown > 10%)
  - 0.0 (halt mode, drawdown > 15% or daily loss > 2%)

### Supported Instruments

- **ES** (E-mini S&P 500): $50 per point, 0.25 tick size
- **NQ** (E-mini NASDAQ-100): $20 per point, 0.25 tick size
- **YM** (E-mini Dow): $5 per point, 1.0 tick size
- **RTY** (E-mini Russell 2000): $50 per point, 0.10 tick size
- **CL** (Crude Oil): $1000 per point, 0.01 tick size
- **GC** (Gold): $100 per point, 0.10 tick size

## 📁 Project Structure

```
trader/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── engines/           # Core trading engines
│   │   │   ├── feature_engine.py      # Technical indicators
│   │   │   ├── strategy_engine.py     # Strategy logic
│   │   │   ├── risk_engine.py         # Position sizing & risk
│   │   │   └── backtest_engine.py     # Event-driven backtest
│   │   └── routers/           # API endpoints
│   │       ├── instruments.py
│   │       ├── bars.py
│   │       ├── features.py
│   │       ├── backtest.py
│   │       ├── signals.py
│   │       ├── portfolio.py
│   │       └── journal.py
│   ├── scripts/               # Utility scripts
│   │   ├── seed_data.py
│   │   ├── ingest_csv.py
│   │   └── run_demo_backtest.py
│   ├── tests/                 # Unit tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── components/        # Shared components
│   │   │   └── Navigation.tsx
│   │   ├── strategy-lab/      # Strategy configuration
│   │   ├── results/           # Backtest results
│   │   ├── signals/           # Live signals
│   │   ├── risk/              # Risk console
│   │   └── journal/           # Trading journal
│   ├── lib/
│   │   └── api.ts             # API client
│   ├── package.json
│   └── Dockerfile
│
├── data/                       # Sample data files
│   └── sample_data/
│       ├── ES_sample.csv
│       └── NQ_sample.csv
│
├── docker-compose.yml          # Docker orchestration
└── README.md                   # This file
```

## 🔌 API Documentation

### Base URL
- Local: `http://localhost:8432`
- API Docs: `http://localhost:8432/docs`

### Key Endpoints

#### Instruments
- `GET /instruments` - List all instruments
- `GET /instruments/{id}` - Get instrument details
- `POST /instruments` - Create new instrument

#### Bars
- `GET /bars/{instrument_id}` - Get OHLCV data
- `POST /bars/ingest` - Ingest bar data from CSV

#### Features
- `GET /features/{instrument_id}` - Get computed features
- `POST /features/recompute/{instrument_id}` - Recompute features
- `POST /features/recompute-all` - Recompute all features

#### Backtests
- `POST /backtest/run` - Create and run backtest
- `GET /backtest/runs` - List all backtests
- `GET /backtest/{id}` - Get backtest details
- `GET /backtest/{id}/results` - Get detailed results
- `DELETE /backtest/{id}` - Delete backtest

#### Signals
- `GET /signals/today` - Get today's signals
- `GET /signals/recent?days=7` - Get recent signals

#### Portfolio
- `GET /portfolio/status` - Current portfolio status
- `GET /portfolio/positions` - Current positions
- `GET /portfolio/equity-curve?days=90` - Equity history

#### Journal
- `GET /journal` - List journal entries
- `POST /journal` - Create entry
- `PUT /journal/{id}` - Update entry
- `DELETE /journal/{id}` - Delete entry

## 🧪 Testing

### Run Backend Tests

```bash
# With Docker
docker-compose exec backend pytest

# Local
cd backend
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

### Test Coverage

The test suite covers:
- ✅ Feature calculation (ATR, MA, HH/LL)
- ✅ Strategy signal generation
- ✅ Risk management and position sizing
- ✅ Trend filtering and breakout detection
- ✅ Stop loss calculations
- ✅ Cooldown period logic

## 📈 Sample Workflow

1. **Prepare Data**
   - Seed instruments: `python scripts/seed_data.py`
   - Ingest historical data: `python scripts/ingest_csv.py ES data.csv`
   - Compute features: `POST /features/recompute-all`

2. **Run Backtest**
   - Configure strategy in Strategy Lab UI
   - Select instruments and date range
   - Set risk parameters
   - Run backtest (executes in background)

3. **Analyze Results**
   - View equity curve and drawdown
   - Review performance metrics
   - Examine trade-by-trade details
   - Check signal history

4. **Document Findings**
   - Add journal entries
   - Tag observations
   - Link to specific trades or backtests

5. **Iterate**
   - Adjust parameters
   - Test different instruments
   - Refine risk management

## 🚢 Deployment

### Production Considerations

1. **Database**
   - Use PostgreSQL in production
   - Set up backups and replication
   - Configure connection pooling

2. **Environment Variables**
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   USE_SQLITE=false
   DEBUG=false
   ```

3. **Security**
   - Add authentication (JWT tokens)
   - Enable HTTPS
   - Configure CORS properly
   - Use secrets management

4. **Performance**
   - Enable Redis caching
   - Set up CDN for frontend
   - Use production builds
   - Configure horizontal scaling

5. **Monitoring**
   - Add logging (ELK stack)
   - Set up metrics (Prometheus/Grafana)
   - Configure alerts
   - Track API performance

## 📝 Configuration

### Environment Variables

**Backend (`backend/.env`)**
```env
DATABASE_URL=postgresql://trader:trader123@postgres:5432/volatility_edge
USE_SQLITE=false
DEBUG=true
DEFAULT_RISK_PER_TRADE=0.005
MAX_DRAWDOWN_WARNING=0.10
MAX_DRAWDOWN_HALT=0.15
MAX_DAILY_LOSS=0.02
```

**Frontend**
```env
NEXT_PUBLIC_API_URL=http://localhost:8432
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is provided as-is for educational and research purposes.

## ⚠️ Disclaimer

This software is for educational purposes only. Trading futures involves substantial risk of loss. Past performance is not indicative of future results. Use at your own risk.

## 🙏 Acknowledgments

- Built with modern best practices for production trading systems
- Inspired by professional quant trading methodologies
- Designed for both backtesting and live trading capabilities

## 📞 Support

For questions, issues, or suggestions:
- **Troubleshooting**: See `TROUBLESHOOTING.md` for common issues and solutions
- **Testing**: See `TESTING_GUIDE.md` for comprehensive testing procedures
- **Data**: See `DATA_GUIDE.md` for data sources and ingestion
- **Trader Guide**: See `TRADER_GUIDE.md` for how to use the application
- **Acronyms**: See `README-ACRONYMS.md` for all technical terms
- **API Docs**: http://localhost:8432/docs
- Open an issue on GitHub
- Check the test suite for usage examples

## 🔌 Port Configuration

The application uses the following ports:
- **Frontend**: 3847
- **Backend API**: 8432
- **PostgreSQL**: 5432

To change these ports, update `docker-compose.yml` and the environment variables.

---

**Happy Trading! 🚀📈**

