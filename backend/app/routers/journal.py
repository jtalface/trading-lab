"""Trading journal endpoints."""
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JournalEntry
from app.schemas import (
    JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse
)

router = APIRouter(prefix="/journal", tags=["journal"])


@router.get("", response_model=List[JournalEntryResponse])
def list_journal_entries(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List journal entries."""
    query = db.query(JournalEntry)
    
    if start_date:
        query = query.filter(JournalEntry.date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.date <= end_date)
    
    query = query.order_by(JournalEntry.date.desc()).limit(limit)
    return query.all()


@router.get("/{entry_id}", response_model=JournalEntryResponse)
def get_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Get journal entry by ID."""
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


@router.post("", response_model=JournalEntryResponse, status_code=201)
def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new journal entry."""
    db_entry = JournalEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.put("/{entry_id}", response_model=JournalEntryResponse)
def update_journal_entry(
    entry_id: int,
    entry: JournalEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update a journal entry."""
    db_entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    update_data = entry.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entry, key, value)
    
    db.commit()
    db.refresh(db_entry)
    return db_entry


@router.delete("/{entry_id}", status_code=204)
def delete_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Delete a journal entry."""
    db_entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    db.delete(db_entry)
    db.commit()
    return None

