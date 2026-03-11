from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.db_models import Household
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_household(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        household_id: str = payload.get("sub")
        if household_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    household = db.query(Household).filter(Household.id == int(household_id)).first()
    if household is None:
        raise credentials_exception
    return household
