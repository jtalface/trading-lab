"""Feature computation endpoints."""
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Instrument, Feature
from app.schemas import FeatureResponse
from app.engines.feature_engine import FeatureEngine

router = APIRouter(prefix="/features", tags=["features"])


@router.get("/{instrument_id}", response_model=List[FeatureResponse])
def get_features(
    instrument_id: int,
    start_date: date = None,
    end_date: date = None,
    limit: int = 500,
    db: Session = Depends(get_db)
):
    """Get computed features for an instrument."""
    query = db.query(Feature).filter(Feature.instrument_id == instrument_id)
    
    if start_date:
        query = query.filter(Feature.date >= start_date)
    if end_date:
        query = query.filter(Feature.date <= end_date)
    
    query = query.order_by(Feature.date.desc()).limit(limit)
    return query.all()


@router.post("/recompute/{instrument_id}")
def recompute_features(
    instrument_id: int,
    db: Session = Depends(get_db)
):
    """Recompute all features for an instrument."""
    instrument = db.query(Instrument).filter(Instrument.id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    
    engine = FeatureEngine()
    count = engine.recompute_features_for_instrument(db, instrument)
    
    return {
        "message": f"Successfully recomputed features for {instrument.symbol}",
        "features_computed": count
    }


@router.post("/recompute-all")
def recompute_all_features(
    db: Session = Depends(get_db)
):
    """Recompute features for all active instruments."""
    instruments = db.query(Instrument).filter(Instrument.active == True).all()
    
    engine = FeatureEngine()
    results = {}
    
    for instrument in instruments:
        count = engine.recompute_features_for_instrument(db, instrument)
        results[instrument.symbol] = count
    
    return {
        "message": "Successfully recomputed features for all instruments",
        "results": results
    }

