"""Bar data and ingest endpoints."""
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bar, Instrument
from app.schemas import BarResponse, BarIngestRequest, BarCreate

router = APIRouter(prefix="/bars", tags=["bars"])


@router.get("/{instrument_id}", response_model=List[BarResponse])
def get_bars(
    instrument_id: int,
    start_date: date = None,
    end_date: date = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Get bars for an instrument."""
    query = db.query(Bar).filter(Bar.instrument_id == instrument_id)
    
    if start_date:
        query = query.filter(Bar.date >= start_date)
    if end_date:
        query = query.filter(Bar.date <= end_date)
    
    query = query.order_by(Bar.date.desc()).limit(limit)
    return query.all()


@router.post("/ingest", status_code=201)
def ingest_bars(
    request: BarIngestRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest bar data for an instrument.
    Creates or updates bars for the given symbol.
    """
    # Get instrument
    instrument = db.query(Instrument).filter(Instrument.symbol == request.symbol).first()
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {request.symbol} not found")
    
    bars_created = 0
    bars_updated = 0
    
    for bar_data in request.bars:
        # Check if bar already exists
        existing_bar = db.query(Bar).filter(
            Bar.instrument_id == instrument.id,
            Bar.date == bar_data.date
        ).first()
        
        if existing_bar:
            # Update existing bar
            existing_bar.open = bar_data.open
            existing_bar.high = bar_data.high
            existing_bar.low = bar_data.low
            existing_bar.close = bar_data.close
            existing_bar.volume = bar_data.volume
            bars_updated += 1
        else:
            # Create new bar
            new_bar = Bar(
                instrument_id=instrument.id,
                **bar_data.model_dump()
            )
            db.add(new_bar)
            bars_created += 1
    
    db.commit()
    
    return {
        "message": f"Successfully ingested bars for {request.symbol}",
        "bars_created": bars_created,
        "bars_updated": bars_updated,
        "total": bars_created + bars_updated
    }

