from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_current_admin
from database import get_db
import models

from schemas import UserOut, UserUpdate

router = APIRouter()

# ----------------------
# CRUD USERS
# ----------------------
@router.get("/users/{user_id}", tags=["User"], response_model=UserOut)
def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Retrieves a user by their ID (admin only)."""

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.get("/users", tags=["User"])
def list_all_users(
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)
):
    """Lists all users (admin only)."""
    users = db.query(models.User).all()

    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "username": user.username,
            "money": user.money,
            "is_admin": user.is_admin
        })

    return {
        "total_users": len(users_list),
        "users": users_list
    }

@router.put("/users/{user_id}", tags=["User"], response_model=UserOut)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Modifies an existing user (admin only)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username is not None:
        db_user.username = user.username

    if user.money is not None:
        db_user.money = user.money

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}", tags=["User"])
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Delete a user (admin only)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
