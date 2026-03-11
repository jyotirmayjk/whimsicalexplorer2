from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import HouseholdCreate, HouseholdResponse, HouseholdSettingsBase, AuthToken
from app.models.db_models import Household, HouseholdSettings
from datetime import datetime, timedelta
import jwt
from app.core.config import settings

router = APIRouter()

# Stub out real Password/Household management for MVP
# Creating a naive login that mints a token for a given household name
@router.post("/login", response_model=dict)
def login(household_data: HouseholdCreate, db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.name == household_data.name).first()
    
    if not household:
        # Auto-provision on first sign-in for demo fluidity
        household = Household(name=household_data.name)
        db.add(household)
        db.flush()
        
        default_settings = HouseholdSettings(household_id=household.id)
        db.add(default_settings)
        db.commit()
        db.refresh(household)
        
    # Generate Bearer JWT
    payload = {
        "sub": str(household.id),
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    return {
         "data": {
             "access_token": encoded_jwt,
             "token_type": "bearer",
             "household": {"id": household.id, "name": household.name}
         }
    }
