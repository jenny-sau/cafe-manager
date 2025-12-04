from sqlalchemy.orm import Session
import models


def log_action(
        db: Session,
        user_id: int,
        action_type: str,
        message: str,
        amount: float = None
):
    """Enregistre une action dans le GameLog et met à jour PlayerProgress."""

    # 1. Créer le log
    db_gameLog = models.GameLog(
        user_id=user_id,
        action_type=action_type,
        message=message,
        amount=amount
    )
    db.add(db_gameLog)

    # 2. Récupérer ou créer PlayerProgress
    progress = db.query(models.PlayerProgress).filter(
        models.PlayerProgress.user_id == user_id
    ).first()

    if not progress:
        # Créer un nouveau PlayerProgress avec toutes les valeurs
        progress = models.PlayerProgress(
            user_id=user_id,
            total_money_earned=0.0,
            total_orders=0,
            current_level=1,
            total_money_spent=0.0
        )
        db.add(progress)
        db.flush()  # Force la création immédiate

    # 3. Mettre à jour les stats selon le type d'action
    if action_type == "order_client" and amount:
        progress.total_money_earned += amount
        progress.total_orders += 1

    elif action_type == "restock" and amount:
        progress.total_money_spent += abs(amount)

    # 4. Calculer le niveau
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

    # Si le niveau a augmenté, logger
    if progress.current_level > old_level:
        level_up_log = models.GameLog(
            user_id=user_id,
            action_type="level_up",
            message=f"BRAVO! Niveau {progress.current_level} atteint !",
            amount=None
        )
        db.add(level_up_log)


    # 5. Commit
    db.commit()