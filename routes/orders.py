from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from dependencies import get_current_admin, get_current_user, log_action
from schemas import OrderCreate, OrderCreatedOut, OrderDetailOut, OrderStatusOut, PaginatedAdminOrdersOut, OrderStatusEnum
import models
from decimal import Decimal
import math

router = APIRouter()

# ----------------------
# CRUD CLIENT'S ORDER
# ----------------------
@router.post(
    "/order/client", tags=["Order"],
    response_model=OrderCreatedOut)
def order_for_client(
        order_data: OrderCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Place an order for a customer. The order is placed on hold."""

    # checks and stock
    menu_items = {}
    for item in order_data.items:
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == item.menu_item_id
        ).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail="Item not found")
        menu_items[item.menu_item_id] = menu_item

    #  Create the order only if everything is valid
    order = models.Order(
        user_id=current_user.id,
        status=models.OrderStatus.PENDING
    )
    db.add(order)
    db.flush()

    # Create the command lines
    response_items = []
    for item in order_data.items:
        menu_item = menu_items[item.menu_item_id]  #  already in memory

        order_item = models.OrderItem(
            order_id=order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
        )
        db.add(order_item)

        response_items.append(
            {"menu_item_name": menu_item.name,
             "menu_item_id": menu_item.id,
             "quantity": item.quantity}
        )

        log_action(
            db=db,
            user_id=current_user.id,
            action_type="order_created",
            message=f"New order : {item.quantity}x {menu_item.name}"
        )

    db.commit()

    return {
        "message": "Order placed",
        "order_id": order.id,
        "items": response_items
    }


@router.get(
    "/orders/{order_id}",
    tags=["Order"],
    response_model=OrderDetailOut)
def read_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """View order details."""
    order = (db.query(models.Order)
             .filter(models.Order.id == order_id)
             .first())

    # Verification:
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")

    items = (db.query(models.OrderItem)
             .options(joinedload(models.OrderItem.menu_item))
             .filter(models.OrderItem.order_id == order_id)
             .all())

    items_response = []
    for item in items:
        items_response.append(
            {"menu_item_id": item.menu_item.id,
             "menu_item_name": item.menu_item.name,
             "quantity": item.quantity}
        )

    return {
        "status" : order.status,
        "items" : items_response
    }

@router.patch("/orders/{order_id}/complete", tags=["Order"], response_model=OrderStatusOut)
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Changes the status of an order from PENDING to COMPLETED. Removes the stock, adds the money to the player, and logs the action."""

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    # Verification:
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    if order.status != models.OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order is not pending")

    order_items = (db.query(models.OrderItem).
                   options(joinedload(models.OrderItem.menu_item))
                   .filter(models.OrderItem.order_id == order_id)
                   .all())

    total = Decimal("0.00")
    for item in order_items:
        inventory = (db.query(models.Inventory).filter(
            models.Inventory.user_id == current_user.id,
            models.Inventory.menu_item_id == item.menu_item_id
        )
        .with_for_update()
        .first())

        if not inventory or inventory.quantity < item.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        #Effect
        amount = item.menu_item.selling_price * item.quantity
        total+=amount
        log_action(
            db=db,
            user_id=current_user.id,
            action_type="order_completed",
            message=f"Commande complétée : {item.quantity}x {item.menu_item.name} (+{amount}€)"
        )
        inventory.quantity -= item.quantity



    try:
        log_action(
            db=db,
            user_id=current_user.id,
            action_type="order_completed",
            message=f"Total commande #{order.id} : +{total}€",
            amount=total
        )

        order.status = models.OrderStatus.COMPLETED
        current_user.money += total
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Order processing failed")

    return {
    "message": "Order completed",
    "order_id" : order.id
    }

@router.patch("/orders/{order_id}/cancel", tags=["Order"], response_model=OrderStatusOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Changes the status of an order from PENDING to CANCELLED. The player failed to complete the order in time; the order is canceled."""

    #Checks
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    if order.status != models.OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order is not pending")

    log_action(
        db=db,
        user_id=current_user.id,
        action_type="order_cancelled",
        message=f"Commande annulée : {order_id} "
        )

    try:
        order.status = models.OrderStatus.CANCELLED
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Order processing failed")

    return {
        "message": "Order cancelled",
        "order_id": order.id
    }

@router.get("/admin/orders", tags=["Order"], response_model=PaginatedAdminOrdersOut)
def list_all_orders(
    page: int = 1,
    limit: int = 20,
    status: OrderStatusEnum | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Lists all commands for all players (admin only)."""

    query = db.query(models.Order)
    if status:
        query = query.filter(models.Order.status == status)
    if user_id is not None:
        query = query.filter(models.Order.user_id == user_id)

    total_items = query.count()

    orders = (
        query
        .order_by(models.Order.created_at.desc())
        .limit(limit)
        .offset((page - 1) * limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": math.ceil(total_items / limit) if limit > 0 else 0,
        "items": orders
    }