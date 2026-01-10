"""Portfolio and risk status endpoints."""
from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Position, PortfolioSnapshot, Instrument
from app.schemas import (
    PositionResponse, PositionWithInstrument,
    PortfolioSnapshotResponse, RiskStatus
)
from app.engines.risk_engine import RiskEngine, RiskConfig

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/status")
def get_portfolio_status(
    db: Session = Depends(get_db)
):
    """Get current portfolio status including risk metrics."""
    today = date.today()
    
    # Get latest snapshot
    latest_snapshot = db.query(PortfolioSnapshot).filter(
        PortfolioSnapshot.backtest_run_id == None
    ).order_by(PortfolioSnapshot.date.desc()).first()
    
    if not latest_snapshot:
        return {
            "message": "No portfolio data available",
            "equity": 0,
            "positions": [],
            "risk_status": None
        }
    
    # Get current positions
    positions = db.query(Position).filter(
        Position.backtest_run_id == None,
        Position.date == latest_snapshot.date
    ).join(Instrument).all()
    
    positions_list = []
    for pos in positions:
        pos_dict = pos.__dict__.copy()
        pos_dict['instrument'] = pos.instrument
        positions_list.append(pos_dict)
    
    # Calculate risk status
    yesterday = today - timedelta(days=1)
    yesterday_snapshot = db.query(PortfolioSnapshot).filter(
        PortfolioSnapshot.backtest_run_id == None,
        PortfolioSnapshot.date == yesterday
    ).first()
    
    start_of_day_equity = yesterday_snapshot.equity if yesterday_snapshot else latest_snapshot.equity
    
    risk_engine = RiskEngine(RiskConfig())
    risk_state = risk_engine.calculate_risk_state(
        current_equity=latest_snapshot.equity,
        peak_equity=latest_snapshot.equity,  # Should track peak separately
        daily_pnl=latest_snapshot.daily_pnl,
        start_of_day_equity=start_of_day_equity
    )
    
    risk_status = RiskStatus(
        current_equity=risk_state.equity,
        peak_equity=risk_state.peak_equity,
        current_drawdown=risk_state.drawdown_pct,
        daily_pnl=risk_state.daily_pnl,
        daily_pnl_pct=risk_state.daily_loss_pct,
        risk_mode=risk_state.mode.value,
        can_open_new_trades=risk_state.can_open_new_trades,
        active_positions=len(positions),
        total_exposure=latest_snapshot.total_exposure,
        message=risk_state.message
    )
    
    return {
        "snapshot": latest_snapshot,
        "positions": positions_list,
        "risk_status": risk_status
    }


@router.get("/positions", response_model=List[PositionWithInstrument])
def get_current_positions(
    db: Session = Depends(get_db)
):
    """Get current positions."""
    # Get latest date with positions
    latest_date = db.query(Position.date).filter(
        Position.backtest_run_id == None
    ).order_by(Position.date.desc()).first()
    
    if not latest_date:
        return []
    
    positions = db.query(Position).filter(
        Position.backtest_run_id == None,
        Position.date == latest_date[0]
    ).join(Instrument).all()
    
    result = []
    for pos in positions:
        pos_dict = pos.__dict__.copy()
        pos_dict['instrument'] = pos.instrument
        result.append(pos_dict)
    
    return result


@router.get("/equity-curve", response_model=List[PortfolioSnapshotResponse])
def get_equity_curve(
    days: int = 365,
    db: Session = Depends(get_db)
):
    """Get portfolio equity curve."""
    cutoff_date = date.today() - timedelta(days=days)
    
    snapshots = db.query(PortfolioSnapshot).filter(
        PortfolioSnapshot.backtest_run_id == None,
        PortfolioSnapshot.date >= cutoff_date
    ).order_by(PortfolioSnapshot.date).all()
    
    return snapshots

