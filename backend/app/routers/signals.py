"""Trading signals endpoints."""
from typing import List
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Signal, Instrument
from app.schemas import SignalResponse, SignalWithInstrument

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/today", response_model=List[SignalWithInstrument])
def get_today_signals(
    db: Session = Depends(get_db)
):
    """Get today's trading signals across all instruments."""
    today = date.today()
    
    signals = db.query(Signal).filter(
        Signal.date == today,
        Signal.backtest_run_id == None  # Only live signals, not backtest signals
    ).join(Instrument).all()
    
    # Attach instrument info
    result = []
    for signal in signals:
        signal_dict = signal.__dict__.copy()
        signal_dict['instrument'] = signal.instrument
        result.append(signal_dict)
    
    return result


@router.get("/recent", response_model=List[SignalWithInstrument])
def get_recent_signals(
    days: int = 7,
    limit: int = 100,
    include_backtest: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get recent trading signals.
    If include_backtest=True (default), includes signals from backtests.
    If False, only shows live trading signals.
    """
    cutoff_date = date.today() - timedelta(days=days)
    
    query = db.query(Signal).filter(Signal.date >= cutoff_date)
    
    # If not including backtest signals, filter them out
    if not include_backtest:
        query = query.filter(Signal.backtest_run_id == None)
    
    signals = query.join(Instrument).order_by(Signal.date.desc()).limit(limit).all()
    
    result = []
    for signal in signals:
        signal_dict = signal.__dict__.copy()
        signal_dict['instrument'] = signal.instrument
        result.append(signal_dict)
    
    return result


@router.get("/latest-backtest", response_model=List[SignalWithInstrument])
def get_latest_backtest_signals(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get signals from the most recent completed backtest that generated signals."""
    from app.models import BacktestRun
    from sqlalchemy import desc, func
    
    # Get the most recent completed backtest that has signals
    backtest_with_signals = db.query(
        BacktestRun.id
    ).filter(
        BacktestRun.status == 'completed'
    ).join(
        Signal, Signal.backtest_run_id == BacktestRun.id
    ).group_by(
        BacktestRun.id
    ).having(
        func.count(Signal.id) > 0
    ).order_by(desc(BacktestRun.id)).first()
    
    if not backtest_with_signals:
        return []
    
    # Get signals from that backtest
    signals = db.query(Signal).filter(
        Signal.backtest_run_id == backtest_with_signals.id
    ).join(Instrument).order_by(Signal.date.desc()).limit(limit).all()
    
    result = []
    for signal in signals:
        signal_dict = signal.__dict__.copy()
        signal_dict['instrument'] = signal.instrument
        result.append(signal_dict)
    
    return result


@router.get("/{signal_id}", response_model=SignalResponse)
def get_signal(
    signal_id: int,
    db: Session = Depends(get_db)
):
    """Get signal by ID."""
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal

