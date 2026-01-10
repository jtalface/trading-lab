"""Backtest execution and results endpoints."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BacktestRun, PortfolioSnapshot, Signal, Position
from app.schemas import (
    BacktestCreateRequest, BacktestResponse, BacktestResults,
    PortfolioSnapshotResponse, SignalResponse, PositionResponse
)
from app.engines.backtest_engine import BacktestEngine

router = APIRouter(prefix="/backtest", tags=["backtest"])


def run_backtest_task(backtest_id: int, config_dict: dict):
    """Background task to run backtest."""
    from app.database import SessionLocal
    from datetime import date
    db = SessionLocal()
    try:
        backtest_run = db.query(BacktestRun).filter(BacktestRun.id == backtest_id).first()
        if backtest_run:
            from app.schemas import BacktestConfig
            # Convert date strings back to date objects if needed
            if isinstance(config_dict.get('start_date'), str):
                config_dict['start_date'] = date.fromisoformat(config_dict['start_date'])
            if isinstance(config_dict.get('end_date'), str):
                config_dict['end_date'] = date.fromisoformat(config_dict['end_date'])
            
            config = BacktestConfig(**config_dict)
            engine = BacktestEngine(db)
            engine.run_backtest(backtest_run, config)
    finally:
        db.close()


@router.post("/run", response_model=BacktestResponse, status_code=202)
def create_backtest(
    request: BacktestCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create and run a new backtest.
    Returns immediately with status='pending' and runs in background.
    """
    # Create backtest run record
    backtest_run = BacktestRun(
        name=request.name,
        description=request.description,
        start_date=request.config.start_date,
        end_date=request.config.end_date,
        config=request.config.model_dump(mode='json'),  # Use JSON serialization mode
        initial_capital=request.config.initial_capital,
        status="pending"
    )
    
    db.add(backtest_run)
    db.commit()
    db.refresh(backtest_run)
    
    # Run backtest in background
    background_tasks.add_task(
        run_backtest_task,
        backtest_run.id,
        request.config.model_dump(mode='json')
    )
    
    return backtest_run


@router.get("/runs", response_model=List[BacktestResponse])
def list_backtests(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all backtest runs."""
    runs = db.query(BacktestRun).order_by(BacktestRun.created_at.desc()).limit(limit).all()
    return runs


@router.get("/{backtest_id}", response_model=BacktestResponse)
def get_backtest(
    backtest_id: int,
    db: Session = Depends(get_db)
):
    """Get backtest run details."""
    backtest = db.query(BacktestRun).filter(BacktestRun.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return backtest


@router.get("/{backtest_id}/results", response_model=BacktestResults)
def get_backtest_results(
    backtest_id: int,
    db: Session = Depends(get_db)
):
    """Get complete backtest results including equity curve and trades."""
    backtest = db.query(BacktestRun).filter(BacktestRun.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    # Fetch related data
    snapshots = db.query(PortfolioSnapshot).filter(
        PortfolioSnapshot.backtest_run_id == backtest_id
    ).order_by(PortfolioSnapshot.date).all()
    
    signals = db.query(Signal).filter(
        Signal.backtest_run_id == backtest_id
    ).order_by(Signal.date).all()
    
    positions = db.query(Position).filter(
        Position.backtest_run_id == backtest_id
    ).order_by(Position.date).all()
    
    # Build metrics dict
    metrics = {
        "total_return": backtest.total_return,
        "cagr": backtest.cagr,
        "sharpe_ratio": backtest.sharpe_ratio,
        "sortino_ratio": backtest.sortino_ratio,
        "max_drawdown": backtest.max_drawdown,
        "max_drawdown_duration_days": backtest.max_drawdown_duration,
        "win_rate": backtest.win_rate,
        "profit_factor": backtest.profit_factor,
        "total_trades": backtest.total_trades,
        "initial_capital": backtest.initial_capital,
        "final_equity": backtest.final_equity,
    }
    
    return BacktestResults(
        backtest=backtest,
        portfolio_snapshots=snapshots,
        signals=signals,
        positions=positions,
        metrics=metrics
    )


@router.delete("/{backtest_id}", status_code=204)
def delete_backtest(
    backtest_id: int,
    db: Session = Depends(get_db)
):
    """Delete a backtest run and all associated data."""
    backtest = db.query(BacktestRun).filter(BacktestRun.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    db.delete(backtest)
    db.commit()
    return None

