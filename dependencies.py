# dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
import models
from auth import decode_access_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token incorrect")

    user_id = payload["user_id"]
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_admin(
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé : Vous devez être admin")
    return current_user

#-------------------------------------

from decimal import Decimal
import models

def log_action(
    db,
    user_id: int,
    action_type: str,
    message: str,
    amount: Decimal = Decimal("0.00")
):
    log = models.GameLog(
        user_id=user_id,
        action_type=action_type,
        message=message,
        amount=amount
    )
    db.add(log)

    progress = db.query(models.PlayerProgress).filter(
        models.PlayerProgress.user_id == user_id
    ).first()

    if not progress:
        progress = models.PlayerProgress(
            user_id=user_id,
            total_money_earned=Decimal("0.00"),
            total_money_spent=Decimal("0.00"),
            total_orders=0,
            current_level=1
        )
        db.add(progress)

    if amount > Decimal("0.00"):
        progress.total_money_earned += amount
        progress.total_orders += 1
    else:
        progress.total_money_spent += abs(amount)
