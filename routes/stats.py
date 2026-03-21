from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_admin, get_current_user
from schemas import GameHistoryOut, PlayerHistoryInfo, PlayerStatsOut, PlayerStatsInfo, PlayerStatsDetails
from sqlalchemy import func
import models

router = APIRouter()

# --------------------------
# CRUD FOR GAME STATISTICS
# --------------------------

@router.get("/admin/stats", tags=["Stats"])
def get_global_stats(
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)  #Admin requis
):
    """Overall game statistics (admin only)."""

    # Count users
    total_users = db.query(models.User).count()
    total_admins = db.query(models.User).filter(models.User.is_admin == True).count()

    # Count the products
    total_menu_items = db.query(models.MenuItem).count()

    # Count orders
    total_orders = db.query(models.Order).count()

    # Total cash in circulation
    total_money = db.query(models.User).with_entities(
        func.sum(models.User.money)
    ).scalar() or 0

    return {
        "users": {
            "total": total_users,
            "admins": total_admins,
            "players": total_users - total_admins
        },
        "game": {
            "total_menu_items": total_menu_items,
            "total_orders": total_orders,
            "total_money_in_game": round(total_money, 2)
        }
    }

@router.get("/game/history", tags=["Stats"], response_model=GameHistoryOut)
def get_game_history(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Retrieves the player's complete action history."""

    logs = db.query(models.GameLog).filter(
        models.GameLog.user_id == current_user.id
    ).order_by(
        models.GameLog.timestamp.desc()
    ).all()

    return GameHistoryOut(
        player=PlayerHistoryInfo(
            username=current_user.username,
            money=current_user.money
        ),
        total_actions=len(logs),
        history=logs
    )

@router.get("/game/stats", tags=["Stats"], response_model=PlayerStatsOut)
def get_game_stats(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Retrieves the player's cumulative statistics."""

    # Retrieve or create PlayerProgress8
    progress = db.query(models.PlayerProgress).filter(
        models.PlayerProgress.user_id == current_user.id
    ).first()

    if not progress:
        # If the player doesn't have stats yet, create some
        progress = models.PlayerProgress(user_id=current_user.id)
        db.add(progress)
        db.commit()
        db.refresh(progress)

    # Calculate net profit
    profit = progress.total_money_earned - progress.total_money_spent

    return PlayerStatsOut(
        player=PlayerStatsInfo(
            username=current_user.username,
            current_money=current_user.money,
            level=progress.current_level
        ),
        stats=PlayerStatsDetails(
            total_money_earned=progress.total_money_earned,
            total_money_spent=progress.total_money_spent,
            profit=progress.total_money_earned - progress.total_money_spent,
            total_orders=progress.total_orders
        )
    )

