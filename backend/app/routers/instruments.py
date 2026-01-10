"""Instrument management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Instrument
from app.schemas import InstrumentCreate, InstrumentResponse

router = APIRouter(prefix="/instruments", tags=["instruments"])


@router.get("", response_model=List[InstrumentResponse])
def list_instruments(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all instruments."""
    query = db.query(Instrument)
    if active_only:
        query = query.filter(Instrument.active == True)
    return query.all()


@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument(
    instrument_id: int,
    db: Session = Depends(get_db)
):
    """Get instrument by ID."""
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument


@router.get("/symbol/{symbol}", response_model=InstrumentResponse)
def get_instrument_by_symbol(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get instrument by symbol."""
    instrument = db.query(Instrument).filter(Instrument.symbol == symbol).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument


@router.post("", response_model=InstrumentResponse, status_code=201)
def create_instrument(
    instrument: InstrumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new instrument."""
    # Check if symbol already exists
    existing = db.query(Instrument).filter(Instrument.symbol == instrument.symbol).first()
    if existing:
        raise HTTPException(status_code=400, detail="Instrument with this symbol already exists")
    
    db_instrument = Instrument(**instrument.model_dump())
    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)
    return db_instrument


@router.put("/{instrument_id}", response_model=InstrumentResponse)
def update_instrument(
    instrument_id: int,
    instrument: InstrumentCreate,
    db: Session = Depends(get_db)
):
    """Update an instrument."""
    db_instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not db_instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    for key, value in instrument.model_dump().items():
        setattr(db_instrument, key, value)
    
    db.commit()
    db.refresh(db_instrument)
    return db_instrument


@router.delete("/{instrument_id}", status_code=204)
def delete_instrument(
    instrument_id: int,
    db: Session = Depends(get_db)
):
    """Delete an instrument (soft delete by setting active=False)."""
    db_instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not db_instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    db_instrument.active = False
    db.commit()
    return None

