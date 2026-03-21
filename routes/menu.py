from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_admin, get_current_user
from schemas import MenuItemCreate, MenuItemOut, MenuListResponse, MenuItemUpdate
import math
import models

router = APIRouter()
# ----------------------
# CRUD MENU
# ----------------------
@router.post("/menu", tags=["Menu"],
          response_model=MenuItemOut,
          status_code=status.HTTP_201_CREATED)
def create_menu_item(
        item: MenuItemCreate,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Creates a new menu item (admin only)."""
    db_menu_item = models.MenuItem(
        name=item.name,
        purchase_price=item.purchase_price,
        selling_price= item.selling_price)
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@router.get("/menu/{menu_id}", tags=["Menu"], response_model=MenuItemOut)
def read_menu_item(
        menu_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Retrieves a menu item by its ID."""
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@router.get("/menu", tags=["Menu"], response_model=MenuListResponse)
def list_menu(
        page: int = 1,
        limit: int = 20,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """List all menu items (with pagination)."""
    skip = (page - 1) * limit
    all_items = db.query(models.MenuItem).offset(skip).limit(limit).all()
    total_items = db.query(models.MenuItem).count()
    total_pages = math.ceil(total_items / limit)

    menu_with_stock = []

    for item in all_items:
        stock = db.query(models.Inventory).filter(
            models.Inventory.menu_item_id == item.id
        ).first()

        product_info = {
            "id": item.id,
            "name": item.name,
            "purchase_price": item.purchase_price,
            "selling_price": item.selling_price,
            "stock": stock.quantity if stock else 0,
            "available": "available" if stock and stock.quantity > 0 else "unavailable"
        }

        menu_with_stock.append(product_info)

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": menu_with_stock
    }

@router.put("/menu/{menu_id}", tags=["Menu"], response_model=MenuItemOut)
def update_menu_item(
        menu_id: int,
        menu_item: MenuItemUpdate,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Modifies an item in the existing menu (admin only)."""
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    if menu_item.name is not None:
        db_menu_item.name = menu_item.name
    if menu_item.purchase_price is not None:
        db_menu_item.purchase_price = menu_item.purchase_price
    if menu_item.selling_price is not None:
        db_menu_item.selling_price = menu_item.selling_price

    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@router.delete("/menu/{menu_id}", tags=["Menu"])
def delete_menu_item(
        menu_id: int,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Removes an item from the menu (admin only)."""
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(db_menu_item)
    db.commit()
    return {"message": "Menu item deleted"}
