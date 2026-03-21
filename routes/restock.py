from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user, log_action
from schemas import InventoryItemOut, RestockCreate

import models
router = APIRouter()
# ----------------------
# RESTOCK BY USER
# ----------------------
@router.post("/order/restock", tags=["Restock"], response_model=InventoryItemOut)
def restock_item(
        order: RestockCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """ Place a coffee order. This increases the player's inventory and decreases the player's money, and logs the action."""
    # Lock the user (to secure the money)
    user = (
        db.query(models.User)
        .filter(models.User.id == current_user.id)
        .with_for_update()
        .first()
    )

    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == order.menu_item_id
    ).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    montant_depense = menu_item.purchase_price * order.quantity

    if user.money < montant_depense:
        raise HTTPException(status_code=400, detail="Pas assez d'argent !")

    user.money -= montant_depense
    #Lock the inventory if it exists
    inventory_item = (db.query(models.Inventory).filter(
        models.Inventory.menu_item_id == order.menu_item_id,
        models.Inventory.user_id == user.id
    )
        .with_for_update()
        .first())

    if not inventory_item:
        inventory_item = models.Inventory(
            menu_item_id=order.menu_item_id,
            quantity=order.quantity,
            user_id=current_user.id
        )
        db.add(inventory_item)
    else:
        inventory_item.quantity += order.quantity

    log_action(
        db=db,
        user_id=current_user.id,
        action_type="restock",
        message=f"Réapprovisionnement : {order.quantity}x {menu_item.name} → -{montant_depense:.2f}€",
        amount=-montant_depense
    )

    db.commit()
    db.refresh(inventory_item)

    return inventory_item