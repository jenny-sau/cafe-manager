from sqlalchemy.orm import Session
from decimal import Decimal
import models


def log_action(
        db: Session,
        user_id: int,
        action_type: str,
        message: str,
        amount: Decimal  = None
):
    """Records an action in the GameLog and updates PlayerProgress.."""

    # 1. Create the log
    db_gameLog = models.GameLog(
        user_id=user_id,
        action_type=action_type,
        message=message,
        amount=amount
    )
    db.add(db_gameLog)

    # 2. Retrieve or create PlayerProgress
    progress = db.query(models.PlayerProgress).filter(
        models.PlayerProgress.user_id == user_id
    ).first()

    if not progress:
        # Create a new PlayerProgress with all the values
        progress = models.PlayerProgress(
            user_id=user_id,
            total_money_earned=Decimal("0.00"),
            total_orders=0,
            current_level=1,
            total_money_spent=Decimal("0.00")
        )
        db.add(progress)
        db.flush()  # Force immediate creation

    # 3. Update stats based on the type of action
    if action_type == "order_client" and amount:
        progress.total_money_earned += amount
        progress.total_orders += 1

    elif action_type == "restock" and amount:
        progress.total_money_spent += abs(amount)

    # 4. Calculate the level
    old_level = progress.current_level

    if progress.total_money_earned >= 10000 and progress.total_orders >= 1000:
        progress.current_level = 5
    elif progress.total_money_earned >= 2000 and progress.total_orders >= 200:
        progress.current_level = 4
    elif progress.total_money_earned >= 500 and progress.total_orders >= 50:
        progress.current_level = 3
    elif progress.total_money_earned >= 100 and progress.total_orders >= 10:
        progress.current_level = 2
    else:
        progress.current_level = 1

    # If the level has risen, log it
    if progress.current_level > old_level:
        level_up_log = models.GameLog(
            user_id=user_id,
            action_type="level_up",
            message=f"Congrats! Level {progress.current_level} achieved !",
            amount=None
        )
        db.add(level_up_log)


