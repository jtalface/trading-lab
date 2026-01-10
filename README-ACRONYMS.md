# 📖 Acronyms & Terminology Guide

Complete glossary of all acronyms, abbreviations, and technical terms used in Volatility Edge Lab.

---

## 📊 Futures Instruments

### **ES** - E-mini S&P 500
- **Full Name:** E-mini Standard & Poor's 500 Futures
- **Exchange:** Chicago Mercantile Exchange (CME)
- **What It Tracks:** S&P 500 stock index (largest 500 US companies)
- **Contract Size:** $50 per point
- **Tick Size:** 0.25 points ($12.50 per tick)
- **Trading Symbol:** ES
- **Example:** If ES is at 4,500, one contract controls $225,000 worth of the S&P 500

### **NQ** - E-mini NASDAQ-100
- **Full Name:** E-mini NASDAQ-100 Futures
- **Exchange:** Chicago Mercantile Exchange (CME)
- **What It Tracks:** NASDAQ-100 index (100 largest non-financial companies on NASDAQ)
- **Contract Size:** $20 per point
- **Tick Size:** 0.25 points ($5 per tick)
- **Trading Symbol:** NQ
- **Example:** Heavy tech exposure (Apple, Microsoft, Amazon, Google, etc.)

### **YM** - E-mini Dow
- **Full Name:** E-mini Dow Jones Industrial Average Futures
- **Exchange:** Chicago Board of Trade (CBOT)
- **What It Tracks:** Dow Jones Industrial Average (30 large US companies)
- **Contract Size:** $5 per point
- **Tick Size:** 1.0 points ($5 per tick)
- **Trading Symbol:** YM
- **Example:** Blue chip stocks like Boeing, Coca-Cola, McDonald's

### **RTY** - E-mini Russell 2000
- **Full Name:** E-mini Russell 2000 Futures
- **Exchange:** Chicago Mercantile Exchange (CME)
- **What It Tracks:** Russell 2000 index (2000 small-cap US companies)
- **Contract Size:** $50 per point
- **Tick Size:** 0.10 points ($5 per tick)
- **Trading Symbol:** RTY
- **Example:** Small-cap stocks, more volatile than ES

### **CL** - Crude Oil
- **Full Name:** West Texas Intermediate (WTI) Crude Oil Futures
- **Exchange:** New York Mercantile Exchange (NYMEX)
- **What It Tracks:** Price of crude oil per barrel
- **Contract Size:** 1,000 barrels ($1,000 per point)
- **Tick Size:** 0.01 points ($10 per tick)
- **Trading Symbol:** CL
- **Example:** If CL is at $75, one contract controls 1,000 barrels worth $75,000

### **GC** - Gold
- **Full Name:** Gold Futures
- **Exchange:** COMEX (Commodity Exchange)
- **What It Tracks:** Price of gold per troy ounce
- **Contract Size:** 100 troy ounces ($100 per point)
- **Tick Size:** 0.10 points ($10 per tick)
- **Trading Symbol:** GC
- **Example:** If GC is at $2,000, one contract controls $200,000 worth of gold

---

## 📈 Technical Indicators

### **MA** - Moving Average
- **Full Name:** Moving Average
- **What It Is:** Average price over a specified number of periods
- **Purpose:** Identifies trend direction and support/resistance
- **Example:** MA(50) = average of last 50 closing prices
- **Usage:** "Price above MA(50) = uptrend"

### **ATR** - Average True Range
- **Full Name:** Average True Range
- **What It Is:** Measure of volatility over a period
- **Purpose:** Used for position sizing and stop placement
- **Calculation:** Average of true ranges over N periods
- **Example:** ATR(20) = 50 points means ES typically moves 50 points per day
- **Usage:** "Stop loss = Entry - (2 × ATR)"

### **HH** - Highest High
- **Full Name:** Highest High
- **What It Is:** The highest price reached over a specified period
- **Purpose:** Identifies breakout levels for long entries
- **Example:** HH(20) = highest high of last 20 days
- **Usage:** "Enter long when price breaks above HH(20)"

### **LL** - Lowest Low
- **Full Name:** Lowest Low
- **What It Is:** The lowest price reached over a specified period
- **Purpose:** Identifies breakout levels for short entries
- **Example:** LL(20) = lowest low of last 20 days
- **Usage:** "Enter short when price breaks below LL(20)"

### **EMA** - Exponential Moving Average
- **Full Name:** Exponential Moving Average
- **What It Is:** Weighted moving average that gives more weight to recent prices
- **Purpose:** More responsive to recent price changes than simple MA
- **Note:** Not currently used in default strategy but available for customization

### **SMA** - Simple Moving Average
- **Full Name:** Simple Moving Average
- **What It Is:** Arithmetic mean of prices over a period (what we call "MA")
- **Purpose:** Smooths price data to identify trends
- **Example:** SMA(50) = sum of 50 closes ÷ 50

---

## 📊 Price Data Terms

### **OHLC** - Open, High, Low, Close
- **What It Is:** The four basic price points for any time period
- **Open:** First traded price of the period
- **High:** Highest price during the period
- **Low:** Lowest price during the period
- **Close:** Last traded price of the period
- **Example:** "ES daily OHLC: 4500, 4520, 4495, 4510"

### **OHLCV** - Open, High, Low, Close, Volume
- **What It Is:** OHLC plus trading volume
- **Volume:** Number of contracts traded during the period
- **Purpose:** Complete bar data for analysis
- **Example:** Used in database to store daily bars

### **Tick** - Minimum Price Movement
- **What It Is:** The smallest increment a futures contract can move
- **Purpose:** Determines minimum profit/loss per contract
- **Example:** ES tick = 0.25 points = $12.50 per contract
- **Usage:** "Slippage = 1 tick" means $12.50 cost per ES contract

### **Point** - Price Unit
- **What It Is:** One full unit of price change
- **Example:** ES moving from 4500 to 4501 = 1 point = $50 per contract
- **Math:** 1 point = 4 ticks (for ES)

### **Bar** - Time Period Data
- **What It Is:** Complete OHLCV data for one time period
- **Example:** "Daily bar" = one day's OHLC data
- **Usage:** "Need 60 bars for MA(50)" = need 60 days of data

---

## 💰 Trading & Performance Terms

### **P&L** - Profit and Loss
- **Full Name:** Profit and Loss
- **What It Is:** The money made or lost on trades
- **Types:**
  - **Realized P&L:** Profit/loss on closed trades
  - **Unrealized P&L:** Profit/loss on open positions
- **Example:** "Daily P&L = -$1,500" means lost $1,500 today

### **DD** - Drawdown
- **Full Name:** Drawdown
- **What It Is:** Peak-to-trough decline in account value
- **Calculation:** (Peak Equity - Current Equity) / Peak Equity
- **Example:** Account peak $110K, now $99K → DD = 10%
- **Usage:** "Max DD = 15%" means worst decline was 15%

### **CAGR** - Compound Annual Growth Rate
- **Full Name:** Compound Annual Growth Rate
- **What It Is:** Annualized return assuming compounding
- **Purpose:** Standardizes returns across different time periods
- **Example:** 30% return over 6 months = ~69% CAGR
- **Good Target:** 15-25% CAGR for futures trend-following

### **Sharpe Ratio**
- **Full Name:** Sharpe Ratio (named after William F. Sharpe)
- **What It Is:** Risk-adjusted return measure
- **Calculation:** (Return - Risk-Free Rate) / Standard Deviation
- **Purpose:** Measures return per unit of risk
- **Interpretation:**
  - < 1.0 = Poor risk-adjusted returns
  - 1.0-2.0 = Good
  - 2.0+ = Excellent
- **Example:** Sharpe = 1.85 means good risk-adjusted performance

### **Sortino Ratio**
- **Full Name:** Sortino Ratio (named after Frank A. Sortino)
- **What It Is:** Modified Sharpe ratio using only downside volatility
- **Purpose:** Measures return relative to harmful (downside) risk only
- **Why Better:** Doesn't penalize upside volatility (which is good!)
- **Interpretation:** Higher is better, typically higher than Sharpe
- **Example:** Sortino = 2.41 means excellent downside risk management

### **Win Rate** - Percentage of Winning Trades
- **What It Is:** Percent of trades that are profitable
- **Calculation:** Winning Trades / Total Trades × 100
- **Example:** 8 winners out of 15 trades = 53% win rate
- **Typical:** 40-60% for trend-following strategies
- **Note:** Low win rate is OK if winners are much larger than losers

### **Profit Factor**
- **What It Is:** Ratio of gross profit to gross loss
- **Calculation:** Total Profit from Winners / Total Loss from Losers
- **Example:** $15K profit, $10K loss → Profit Factor = 1.5
- **Interpretation:**
  - < 1.0 = Losing strategy
  - 1.0-1.5 = Marginal
  - 1.5-2.0 = Good
  - 2.0+ = Excellent

### **Payoff Ratio** (aka Reward/Risk Ratio)
- **What It Is:** Average winner divided by average loser
- **Calculation:** Avg Win Size / Avg Loss Size
- **Example:** Avg win $2,000, avg loss $1,000 → Payoff = 2.0
- **Purpose:** Shows if winners are bigger than losers
- **Note:** Trend-following typically has high payoff ratios (2-4+)

---

## 🎯 Strategy Terms

### **Long** - Buy Position
- **What It Is:** Buying a contract expecting price to rise
- **Profit:** When price goes up
- **Loss:** When price goes down
- **Example:** "Long 2 ES at 4500" = bought 2 contracts at 4500

### **Short** - Sell Position
- **What It Is:** Selling a contract expecting price to fall
- **Profit:** When price goes down
- **Loss:** When price goes up
- **Example:** "Short 1 NQ at 15000" = sold 1 contract at 15000

### **Entry** - Opening a Position
- **What It Is:** The act of entering a new trade
- **Types:** Entry Long, Entry Short
- **Example:** "Entry Long signal at 4520"

### **Exit** - Closing a Position
- **What It Is:** The act of closing an existing trade
- **Types:**
  - Normal Exit (strategy signal)
  - Stop Loss Exit (risk management)
  - Time Exit (held too long)
- **Example:** "Exit Long at 4580" = closed long position

### **Stop Loss** (or **Stop**)
- **What It Is:** Pre-defined price to exit losing trade
- **Purpose:** Limits maximum loss on any single trade
- **Example:** "Long at 4500, stop at 4450" = max loss 50 points
- **Usage:** "2× ATR stop" = stop is 2 ATR away from entry

### **Breakout**
- **What It Is:** Price moving beyond a defined level
- **Purpose:** Entry signal indicating trend strength
- **Example:** "Price broke above HH(20)" = bullish breakout
- **Usage:** Our strategy enters on 20-day high/low breakouts

### **Trend-Following**
- **What It Is:** Strategy that profits from sustained price moves
- **Philosophy:** "The trend is your friend"
- **Characteristics:**
  - Low win rate (40-50%)
  - High payoff ratio (winners >> losers)
  - Requires patience
- **Example:** Catch big moves, cut losers quickly

### **Whipsaw**
- **What It Is:** False signal that quickly reverses
- **Result:** Small loss, frustrating but normal
- **Example:** Entry signal → stop hit next day → trend continues
- **Note:** Why we have cooldown periods

### **Cooldown Period**
- **What It Is:** Waiting period after exiting before re-entry
- **Purpose:** Prevents repeated whipsaws
- **Duration:** 3 trading days (in default strategy)
- **Example:** Exit ES Long Monday → can't re-enter until Thursday

---

## 🎲 Risk Management Terms

### **Position Size** (or **Position Sizing**)
- **What It Is:** Number of contracts to trade
- **Purpose:** Controls risk per trade
- **Calculation:** Based on account size, risk %, and stop distance
- **Example:** "$100K account, 0.5% risk, 50 pt stop = 2 contracts"

### **Contract** - Futures Contract
- **What It Is:** One standardized futures agreement
- **Example:** "Trading 2 contracts" = 2 ES futures
- **Value:** Varies by instrument (ES = $50/pt, NQ = $20/pt)

### **Multiplier** (or **Contract Multiplier**)
- **What It Is:** Dollar value per point of price movement
- **Purpose:** Converts points to dollars
- **Examples:**
  - ES: $50/point
  - NQ: $20/point
  - GC: $100/point
- **Usage:** 10 point move × $50 multiplier = $500 per contract

### **Leverage**
- **What It Is:** Controlling large position with small capital
- **Example:** $5K margin controls $225K worth of ES
- **Risk:** Can lose more than initial investment
- **Note:** Why position sizing and stops are critical!

### **Margin**
- **What It Is:** Minimum capital required to hold a position
- **Example:** ES margin ~$12,000 per contract
- **Note:** Not the same as risk (can lose more than margin)

### **Exposure**
- **What It Is:** Total dollar value of open positions
- **Calculation:** Contracts × Price × Multiplier
- **Example:** 2 ES at 4500 = 2 × 4500 × $50 = $450K exposure
- **Limit:** System caps exposure as % of equity

### **Correlation**
- **What It Is:** How two instruments move together
- **Range:** -1 (opposite) to +1 (same direction)
- **Example:** ES and NQ are highly correlated (~0.95)
- **Risk:** High correlation = less diversification
- **Usage:** System limits ES+NQ combined exposure

---

## 🖥️ System & Technical Terms

### **API** - Application Programming Interface
- **Full Name:** Application Programming Interface
- **What It Is:** Interface for programs to communicate
- **Usage:** Access system functionality programmatically
- **Example:** `GET /backtest/runs` returns list of backtests
- **URL:** http://localhost:8432/docs

### **UI** - User Interface
- **Full Name:** User Interface
- **What It Is:** Visual interface for human interaction
- **Components:** Strategy Lab, Results, Signals, Risk Console, Journal
- **URL:** http://localhost:3847

### **REST** - Representational State Transfer
- **Full Name:** REpresentational State Transfer
- **What It Is:** API architecture style
- **Methods:** GET, POST, PUT, DELETE
- **Example:** `POST /backtest/run` creates new backtest

### **JSON** - JavaScript Object Notation
- **Full Name:** JavaScript Object Notation
- **What It Is:** Data format for API communication
- **Example:** `{"symbol": "ES", "price": 4500}`

### **CRUD** - Create, Read, Update, Delete
- **Full Name:** Create, Read, Update, Delete
- **What It Is:** Basic database operations
- **Example:** Journal has full CRUD (create/view/edit/delete entries)

### **CSV** - Comma-Separated Values
- **Full Name:** Comma-Separated Values
- **What It Is:** Simple text file format for data
- **Usage:** Importing historical bar data
- **Example:** `date,open,high,low,close,volume`

### **SQL** - Structured Query Language
- **Full Name:** Structured Query Language
- **What It Is:** Language for database operations
- **Database:** PostgreSQL (production) or SQLite (local)

### **ORM** - Object-Relational Mapping
- **Full Name:** Object-Relational Mapping
- **What It Is:** Converts between database tables and Python objects
- **Library:** SQLAlchemy
- **Example:** `Instrument` Python class ↔️ `instruments` table

---

## 📊 Database & Data Terms

### **Instrument**
- **What It Is:** A tradeable futures contract
- **Examples:** ES, NQ, YM, RTY, CL, GC
- **Attributes:** symbol, name, tick size, multiplier

### **Bar** (or **Candle**)
- **What It Is:** OHLCV data for one time period
- **Storage:** Database table with daily bars
- **Usage:** Input for feature calculation and backtesting

### **Feature**
- **What It Is:** Computed technical indicator
- **Examples:** ATR, MA, slope, HH, LL
- **Storage:** Separate table linked to bars
- **Purpose:** Pre-computed for faster backtesting

### **Signal**
- **What It Is:** Strategy-generated trading opportunity
- **Types:** Entry Long, Entry Short, Exit Long, Exit Short, Stop
- **Storage:** Recorded in database with date, price, reason
- **Usage:** Historical analysis and live trading

### **Order**
- **What It Is:** Instruction to buy or sell
- **Attributes:** Side (buy/sell), quantity, type (market/limit)
- **Status:** Pending, Filled, Cancelled, Rejected

### **Fill** (or **Execution**)
- **What It Is:** Completed order execution
- **Attributes:** Fill price, quantity, commission, slippage
- **Purpose:** Records actual trade execution

### **Position**
- **What It Is:** Currently held contracts
- **Attributes:** Quantity (+ for long, - for short), entry price, stop
- **P&L:** Calculated from entry price vs. current price

### **Snapshot** (or **Portfolio Snapshot**)
- **What It Is:** Daily portfolio state
- **Attributes:** Equity, cash, P&L, drawdown, positions
- **Purpose:** Track portfolio over time, calculate metrics

### **Backtest Run**
- **What It Is:** Complete backtest execution record
- **Attributes:** Config, results, metrics, status
- **Purpose:** Store and compare different strategy tests

---

## 📈 Performance & Metrics

### **Equity**
- **What It Is:** Total account value (cash + positions)
- **Calculation:** Cash + Unrealized P&L
- **Example:** $100K cash + $5K unrealized = $105K equity

### **Equity Curve**
- **What It Is:** Chart of equity over time
- **Purpose:** Visual representation of strategy performance
- **Good Curve:** Smooth upward trend
- **Bad Curve:** Erratic, choppy, downward

### **Max DD** - Maximum Drawdown
- **Full Name:** Maximum Drawdown
- **What It Is:** Largest peak-to-trough decline
- **Example:** Peak $110K → trough $90K → Max DD = 18.2%
- **Purpose:** Shows worst-case loss period

### **DD Duration** - Drawdown Duration
- **Full Name:** Drawdown Duration
- **What It Is:** Time from peak to recovery to new peak
- **Example:** "Max DD duration = 45 days"
- **Purpose:** Shows how long you're underwater

### **Volatility** (or **Vol**)
- **What It Is:** Measure of price fluctuation
- **Calculation:** Standard deviation of returns
- **Purpose:** Risk measurement
- **Usage:** Higher vol = higher risk

### **Alpha**
- **What It Is:** Excess return vs. benchmark
- **Example:** Strategy returns 20%, benchmark returns 15% → Alpha = 5%
- **Note:** Not currently calculated (no benchmark comparison)

### **Beta**
- **What It Is:** Correlation to market/benchmark
- **Example:** Beta = 1.2 means moves 20% more than market
- **Note:** Not currently calculated

---

## 🏗️ Technology Stack

### **FastAPI**
- **What It Is:** Modern Python web framework
- **Purpose:** Backend API server
- **Features:** Fast, auto-docs, async support

### **Next.js**
- **What It Is:** React framework for web apps
- **Purpose:** Frontend UI
- **Features:** Server-side rendering, routing, TypeScript

### **PostgreSQL** (or **Postgres**)
- **What It Is:** Relational database system
- **Purpose:** Production data storage
- **Alternative:** SQLite for local development

### **SQLAlchemy**
- **What It Is:** Python ORM library
- **Purpose:** Database operations in Python
- **Features:** Models, queries, relationships

### **pandas**
- **What It Is:** Python data analysis library
- **Purpose:** Feature calculation, backtesting
- **Features:** DataFrames, time series, calculations

### **Docker**
- **What It Is:** Containerization platform
- **Purpose:** Package app + dependencies
- **Benefits:** Consistent environment, easy deployment

### **Docker Compose**
- **What It Is:** Multi-container orchestration
- **Purpose:** Run postgres + backend + frontend together
- **Usage:** `docker-compose up`

---

## 📐 Mathematical & Statistical Terms

### **Mean** (or **Average**)
- **What It Is:** Sum divided by count
- **Example:** Returns of 5%, 3%, -2% → Mean = 2%
- **Usage:** Average winner, average loser

### **Median**
- **What It Is:** Middle value when sorted
- **Example:** Returns of 5%, 3%, -2% → Median = 3%
- **Purpose:** Less affected by outliers than mean

### **Standard Deviation** (or **Std Dev**)
- **Symbol:** σ (sigma)
- **What It Is:** Measure of spread/dispersion
- **Purpose:** Quantifies volatility
- **Usage:** Used in Sharpe ratio calculation

### **Slope**
- **What It Is:** Rate of change
- **Calculation:** Change in Y / Change in X
- **Example:** MA(50) slope = 0.5 → moving average rising
- **Usage:** "MA slope > 0" = uptrend confirmation

### **Correlation**
- **Symbol:** ρ (rho) or r
- **What It Is:** Statistical relationship between two variables
- **Range:** -1 to +1
- **Example:** ES and NQ correlation = 0.95 (highly correlated)

---

## 🔤 Other Common Abbreviations

### **CTA** - Commodity Trading Advisor
- **Full Name:** Commodity Trading Advisor
- **What It Is:** Professional futures trader/manager
- **Example:** "Many CTAs use trend-following strategies"

### **CME** - Chicago Mercantile Exchange
- **Full Name:** Chicago Mercantile Exchange
- **What It Is:** Largest futures exchange
- **Trades:** ES, NQ, etc.

### **CBOT** - Chicago Board of Trade
- **Full Name:** Chicago Board of Trade
- **What It Is:** Historic futures exchange (now part of CME Group)
- **Trades:** YM, Treasury futures

### **NYMEX** - New York Mercantile Exchange
- **Full Name:** New York Mercantile Exchange
- **What It Is:** Energy and metals futures exchange
- **Trades:** CL (crude oil)

### **COMEX** - Commodity Exchange
- **Full Name:** Commodity Exchange
- **What It Is:** Metals futures exchange
- **Trades:** GC (gold), silver, copper

### **MVP** - Minimum Viable Product
- **Full Name:** Minimum Viable Product
- **What It Is:** First working version with core features
- **This System:** MVP trend-following system ("v1")

### **PnL** - Alternative spelling of P&L
- **Same as:** P&L (Profit and Loss)
- **Usage:** Interchangeable

### **EOD** - End of Day
- **Full Name:** End of Day
- **What It Is:** Daily close of trading
- **Usage:** "EOD data" = daily bars

### **RTH** - Regular Trading Hours
- **Full Name:** Regular Trading Hours
- **What It Is:** Standard market hours (not overnight)
- **Example:** ES RTH = 9:30 AM - 4:00 PM ET

### **TS** - TypeScript
- **Full Name:** TypeScript
- **What It Is:** Typed superset of JavaScript
- **Usage:** Frontend code is written in TypeScript

---

## 🎯 Quick Reference

### Most Important for Traders
1. **ES, NQ** - Main instruments
2. **MA** - Trend filter
3. **ATR** - Volatility measure
4. **HH/LL** - Breakout levels
5. **P&L** - Your money!
6. **DD** - Drawdown (pain metric)
7. **Sharpe** - Risk-adjusted returns

### Most Important for Performance
1. **CAGR** - Annualized returns
2. **Sharpe Ratio** - Risk-adjusted performance
3. **Max DD** - Worst decline
4. **Win Rate** - % winners
5. **Profit Factor** - Winners/losers ratio

### Most Important for Risk
1. **Stop Loss** - Max loss per trade
2. **Position Size** - Number of contracts
3. **Drawdown** - Account decline
4. **Leverage** - Capital efficiency (and risk!)
5. **Exposure** - Total risk

---

## 📚 Want to Learn More?

- **README.md** - Complete technical documentation
- **TRADER_GUIDE.md** - How to use as a trader
- **TESTING_GUIDE.md** - How to test the system
- **Strategy Lab** - Experiment with parameters
- **Journal** - Document your learning

---

**Got questions? Check the docs or experiment in Strategy Lab!** 🚀

