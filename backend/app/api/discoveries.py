from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.db.session import get_db
from app.core.security import get_current_household
from app.models.db_models import Household, Discovery, Session as DBSession
from app.schemas.app_data import DiscoveryResponse

router = APIRouter()

@router.get("/", response_model=dict)
def list_discoveries(household: Household = Depends(get_current_household), db: Session = Depends(get_db)):
    # Get all active sessions for household, then grab discoveries
    discoveries = db.query(Discovery).join(DBSession).filter(DBSession.household_id == household.id).order_by(desc(Discovery.created_at)).all()
    
    response_items = [DiscoveryResponse.model_validate(d).model_dump() for d in discoveries]
    return {"data": response_items}

@router.get("/{discovery_id}", response_model=dict)
def get_discovery(discovery_id: int, household: Household = Depends(get_current_household), db: Session = Depends(get_db)):
    discovery = db.query(Discovery).join(DBSession).filter(Discovery.id == discovery_id, DBSession.household_id == household.id).first()
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery not found")
        
    return {"data": DiscoveryResponse.model_validate(discovery).model_dump()}

@router.post("/{discovery_id}/favorite", response_model=dict)
def toggle_favorite(discovery_id: int, household: Household = Depends(get_current_household), db: Session = Depends(get_db)):
    discovery = db.query(Discovery).join(DBSession).filter(Discovery.id == discovery_id, DBSession.household_id == household.id).first()
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery not found")
        
    discovery.is_favorite = not discovery.is_favorite
    db.commit()
    db.refresh(discovery)
    
    return {"data": DiscoveryResponse.model_validate(discovery).model_dump()}

@router.delete("/{discovery_id}", response_model=dict)
def delete_discovery(discovery_id: int, household: Household = Depends(get_current_household), db: Session = Depends(get_db)):
    discovery = db.query(Discovery).join(DBSession).filter(Discovery.id == discovery_id, DBSession.household_id == household.id).first()
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery not found")
        
    db.delete(discovery)
    db.commit()
    
    return {"data": {"deleted": True}}
