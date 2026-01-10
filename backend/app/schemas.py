"""Pydantic schemas for API request/response validation."""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# Enums
class SignalTypeSchema(str, Enum):
    ENTRY_LONG = "entry_long"
    ENTRY_SHORT = "entry_short"
    EXIT_LONG = "exit_long"
    EXIT_SHORT = "exit_short"
    STOP_LONG = "stop_long"
    STOP_SHORT = "stop_short"


class OrderSideSchema(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatusSchema(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


# Instrument Schemas
class InstrumentBase(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None
    tick_size: float
    multiplier: float
    currency: str = "USD"
    active: bool = True


class InstrumentCreate(InstrumentBase):
    pass


class InstrumentResponse(InstrumentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Bar Schemas
class BarBase(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float = 0


class BarCreate(BarBase):
    instrument_id: int


class BarResponse(BarBase):
    id: int
    instrument_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BarIngestRequest(BaseModel):
    symbol: str
    bars: List[BarBase]


# Feature Schemas
class FeatureResponse(BaseModel):
    id: int
    instrument_id: int
    date: date
    atr_20: Optional[float]
    ma_50: Optional[float]
    ma_slope_10: Optional[float]
    hh_20: Optional[float]
    ll_20: Optional[float]
    hh_10: Optional[float]
    ll_10: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Signal Schemas
class SignalResponse(BaseModel):
    id: int
    instrument_id: int
    date: date
    signal_type: SignalTypeSchema
    price: Optional[float]
    target_contracts: int
    stop_price: Optional[float]
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SignalWithInstrument(SignalResponse):
    instrument: InstrumentResponse


# Position Schemas
class PositionResponse(BaseModel):
    id: int
    instrument_id: int
    date: date
    quantity: int
    entry_price: float
    current_price: Optional[float]
    stop_price: Optional[float]
    unrealized_pnl: float
    
    class Config:
        from_attributes = True


class PositionWithInstrument(PositionResponse):
    instrument: InstrumentResponse


# Portfolio Snapshot Schemas
class PortfolioSnapshotResponse(BaseModel):
    id: int
    date: date
    equity: float
    cash: float
    unrealized_pnl: float
    realized_pnl: float
    daily_pnl: float
    drawdown: float
    total_exposure: float
    num_positions: int
    
    class Config:
        from_attributes = True


# Backtest Schemas
class BacktestConfig(BaseModel):
    """Backtest configuration parameters."""
    instruments: List[str]  # List of symbols
    start_date: date
    end_date: date
    initial_capital: float = 100000.0
    
    # Strategy parameters
    atr_period: int = 20
    ma_period: int = 50
    ma_slope_period: int = 10
    breakout_period: int = 20
    exit_period: int = 10
    stop_atr_multiple: float = 2.0
    cooldown_days: int = 3
    
    # Risk parameters
    risk_per_trade: float = 0.005
    max_contracts_per_instrument: Optional[int] = None
    max_gross_exposure: Optional[float] = None
    max_correlated_exposure: Optional[float] = None  # For ES+NQ
    
    # Execution parameters
    slippage_ticks: float = 1.0
    commission_per_contract: float = 2.50
    entry_timing: str = "next_open"  # next_open, next_close
    
    # Risk guardrails
    drawdown_warning_pct: float = 0.10
    drawdown_halt_pct: float = 0.15
    daily_loss_limit_pct: float = 0.02


class BacktestCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    config: BacktestConfig


class BacktestResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: date
    end_date: date
    config: Dict[str, Any]
    initial_capital: float
    final_equity: Optional[float]
    total_return: Optional[float]
    cagr: Optional[float]
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    max_drawdown: Optional[float]
    max_drawdown_duration: Optional[int]
    win_rate: Optional[float]
    profit_factor: Optional[float]
    total_trades: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BacktestResults(BaseModel):
    """Detailed backtest results."""
    backtest: BacktestResponse
    portfolio_snapshots: List[PortfolioSnapshotResponse]
    signals: List[SignalResponse]
    positions: List[PositionResponse]
    metrics: Dict[str, Any]


# Journal Schemas
class JournalEntryBase(BaseModel):
    date: date
    title: str
    content: str
    tags: Optional[str] = None
    signal_id: Optional[int] = None
    order_id: Optional[int] = None
    backtest_run_id: Optional[int] = None


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None


class JournalEntryResponse(JournalEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Risk Console Schemas
class RiskStatus(BaseModel):
    """Current risk status."""
    current_equity: float
    peak_equity: float
    current_drawdown: float
    daily_pnl: float
    daily_pnl_pct: float
    risk_mode: str  # "normal", "warning", "halt"
    can_open_new_trades: bool
    active_positions: int
    total_exposure: float
    message: str

