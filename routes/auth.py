from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import hash_password, verify_password, create_access_token
from schemas import UserSignup, UserResponse, UserLogin, TokenOut
import os
from limiter import limiter

router = APIRouter()
# --------------------------
# AUTHENTIFICATION
# --------------------------
@router.post(
    "/auth/signup", tags=["Auth"],
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute" if os.getenv("TESTING") != "true" else "1000/minute") # Maximum 5 signups / minute
def signup(
        request: Request,
        user: UserSignup, db: Session = Depends(get_db)
):
    """Create a new user account."""
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed = hash_password(user.password)

    db_user = models.User(
        username=user.username,
        password_hash=hashed,
        money=user.money,
        is_admin = False,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post(
    "/auth/login", tags=["Auth"],
    response_model=TokenOut,
    status_code=status.HTTP_200_OK
)
def login(
        credentials: UserLogin,
        db: Session = Depends(get_db)
):
    """Log in and receive a JWT token."""

    user = db.query(models.User).filter(
        models.User.username == credentials.username
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(data={"user_id": user.id})

    return {
        "access_token": token
    }