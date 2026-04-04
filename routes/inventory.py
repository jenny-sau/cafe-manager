from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from dependencies import get_current_admin, get_current_user
from schemas import InventoryOut, InventoryItemOut, InventoryItemPlayerOut
import models

router = APIRouter()

# ----------------------
# CRUD INVENTORY
# ----------------------
@router.get(
    "/inventory",
    tags=["Inventory"],
    response_model=InventoryOut,
    status_code=status.HTTP_200_OK
)
def list_inventory(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Check the inventory of products that the cafe has in stock."""

    inventory_items = (
        db.query(models.Inventory)
        .options(joinedload(models.Inventory.menu_item))
        .filter(models.Inventory.user_id == current_user.id)
        .all()
    )

    items = [
        InventoryItemPlayerOut(
            menu_item_id=inv.menu_item_id,
            product_name=inv.menu_item.name,
            quantity=inv.quantity
        )
        for inv in inventory_items
    ]

    return InventoryOut(items=items)


@router.get(
    "/inventory/{item_id}",
    tags=["Inventory"],
    response_model=InventoryItemOut,
    status_code=status.HTTP_200_OK
)
def read_inventory(item_id: int,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)
):
    """Retrieves an inventory item by its ID."""
    item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id,
        models.Inventory.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete(
    "/inventory/{item_id}",
    tags=["Inventory"],
    status_code=status.HTTP_200_OK
)
def admin_delete_inventory(
        item_id: int,
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)
):
    """Deletes any inventory item (admin only)."""

    db_item = (db.query(models.Inventory)
               .options(
                        joinedload(models.Inventory.menu_item),
                        joinedload(models.Inventory.user)
                        )
               .filter(models.Inventory.id == item_id)
               .first())

    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    db.delete(db_item)
    db.commit()

    return {
        "message": "Inventory deleted",
        "deleted_item": {
            "id": item_id,
            "product_name": db_item.menu_item.name if db_item.menu_item else "Unknown",
            "quantity": db_item.quantity,
            "owner": db_item.user.username if db_item.user else "Unknown"
        }
    }
