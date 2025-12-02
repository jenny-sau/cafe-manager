from sqlalchemy.orm import Session
import models

def log_action(
    db: Session,
    user_id: int,
    action_type: str,
    message: str,
    amount: float = None
):
    """Enregistre une action dans le GameLog."""
    db_gameLog = models.GameLog(
        user_id=user_id,
        action_type=action_type,
        message=message,
        amount=amount
    )
    db.add(db_gameLog)
    db.commit()