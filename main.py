import math
from decimal import Decimal, ROUND_HALF_UP
from logging import raiseExceptions

from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from schemas import (
    UserCreate, UserOut, UserUpdate, TokenOut,
    MenuItemCreate, MenuItemOut, MenuListResponse, MenuItemWithStock, MenuItemUpdate,
    InventoryCreate, InventoryItemOut, InventoryItemPlayerOut, InventoryOut, InventoryUpdate,
    OrderStatusEnum, OrderCreate, OrderedItemOut, RestockCreate, OrderCreatedOut, OrderStatusOut, OrderDetailOut, PaginatedOrdersOut, OrderSummaryOut, PaginatedAdminOrdersOut,
    UserSignup, UserResponse, UserLogin,
    GameLogOut
)
from database import Base, engine, get_db
import models
from auth import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from dotenv import load_dotenv
load_dotenv(".env")

import os
print("DATABASE_URL =", os.getenv("DATABASE_URL"))


# ----------------------
# CRÉATION DE LA BASE DE DONNÉES
# -> Ne pas utiliser en prod
# La création du schéma est gérée par Alembic
# ----------------------
# Base.metadata.create_all(bind=engine)

# ----------------------
# INITIALISATION DE L'APPLICATION FASTAPI
# ----------------------
app = FastAPI(
    title = "Café Manager API",
    description="API REST pour la gestion d'un café virtuel."
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour dev : autorise tout
    allow_credentials=True,
    allow_methods=["*"],  # Autorise GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Autorise tous les headers
)
# ----------------------
# SÉCURITÉ JWT
# ----------------------
security = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    """Vérifie que l'utilisateur est connecté."""

    # Récupérer le token
    token = credentials.credentials

    # Décoder le token
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token incorrect")

    # Extraire le user_id
    user_id = payload["user_id"]

    # Charger le user depuis la DB
    user = db.query(models.User).filter(models.User.id == user_id).first()

    # Vérifier que le user existe
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def get_current_admin(
    current_user: models.User = Depends(get_current_user)
):
    """Vérifie que l'utilisateur connecté est admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé : Vous devez être admin"
        )
    return current_user

# ----------------------
# LOGS & STATS
# ----------------------
def log_action(
    db: Session,
    user_id: int,
    action_type: str,
    message: str,
    amount: Decimal = Decimal("0.00")
):
    log = models.GameLog(
        user_id=user_id,
        action_type=action_type,
        message=message,
        amount=amount
    )
    db.add(log)

    progress = db.query(models.PlayerProgress).filter(
        models.PlayerProgress.user_id == user_id
    ).first()

    if not progress:
        progress = models.PlayerProgress(
            user_id=user_id,
            total_money_earned=Decimal("0.00"),
            total_money_spent=Decimal("0.00"),
            total_orders=0,
            current_level=1
        )
        db.add(progress)

    if amount > Decimal("0.00"):
        progress.total_money_earned += amount
        progress.total_orders += 1
    else:
        progress.total_money_spent += abs(amount)

# ----------------------
# ROUTES SIMPLES / TEST
# ----------------------
# @app.get("/")
# async def root():
#     """Page d'accueil simple."""
#     return {"message": "Welcome to cafe manager"}


@app.get("/health")
async def health():
    """Vérifie que l'application fonctionne."""
    return {"status": "ok"}

# --------------------------
# AUTHENTIFICATION
# --------------------------
@app.post(
    "/auth/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute") # Maximum 5 signups par minute
def signup(
        request: Request,
        user: UserSignup, db: Session = Depends(get_db)
):
    """Créer un nouveau compte utilisateur."""
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username déjà pris")

    hashed = hash_password(user.password)

    db_user = models.User(
        username=user.username,
        password_hash=hashed,
        money=user.money,
        is_admin = user.is_admin,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post(
    "/auth/login",
    response_model=TokenOut,
    status_code=status.HTTP_200_OK
)
def login(
        credentials: UserLogin,
        db: Session = Depends(get_db)
):
    """Se connecter et recevoir un JWT token."""

    user = db.query(models.User).filter(
        models.User.username == credentials.username
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Username ou password incorrect")

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username ou password incorrect")

    token = create_access_token(data={"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ----------------------
# CRUD UTILISATEURS
# ----------------------
@app.get("/users/{user_id}", response_model=UserOut)
def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Récupère un utilisateur par son ID (admin uniquement)."""

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@app.get("/users")
def list_all_users(
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)
):
    """Liste tous les utilisateurs (admin uniquement)."""
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

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin)
):
    """Modifie un utilisateur existant (admin uniquement)."""
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


@app.delete("/users/{user_id}")
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Supprime un utilisateur (admin uniquemment)."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

# ----------------------
# CRUD MENU
# ----------------------
@app.post("/menu",
          response_model=MenuItemOut,
          status_code=status.HTTP_201_CREATED)
def create_menu_item(
        item: MenuItemCreate,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Crée un nouvel item du menu (admin uniquement)."""
    db_menu_item = models.MenuItem(
        name=item.name,
        purchase_price=item.purchase_price,
        selling_price= item.selling_price)
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@app.get("/menu/{menu_id}", response_model=MenuItemOut)
def read_menu_item(
        menu_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Récupère un item du menu par son ID."""
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.get("/menu", response_model=MenuListResponse)
def list_menu(
        page: int = 1,
        limit: int = 20,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Liste tous les items du menu (avec pagination)."""
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

@app.put("/menu/{menu_id}", response_model=MenuItemOut)
def update_menu_item(
        menu_id: int,
        menu_item: MenuItemUpdate,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Modifie un item du menu existant (admin uniquement)."""
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


@app.delete("/menu/{menu_id}")
def delete_menu_item(
        menu_id: int,
        db: Session = Depends(get_db),
        admin: models.User = Depends(get_current_admin)
):
    """Supprime un item du menu (admin uniquement)."""
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(db_menu_item)
    db.commit()
    return {"message": "Menu item deleted"}

# ----------------------
# RÉAPPROVISIONNEMENT PAR LE JOUEUR
# ----------------------
@app.post("/order/restock", response_model=InventoryItemOut)
def restock_item(
        order: RestockCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
        Passe une commande pour le café.
        Cela augmente le stock de l'inventaire du joueur et diminue l'argent au joueur et log l'action.
        """

    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == order.menu_item_id
    ).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    montant_depense = menu_item.purchase_price * order.quantity

    if current_user.money < montant_depense:
        raise HTTPException(status_code=400, detail="Pas assez d'argent !")

    current_user.money -= montant_depense

    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.menu_item_id == order.menu_item_id,
        models.Inventory.user_id == current_user.id
    ).first()

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

# ----------------------
# CRUD INVENTAIRE
# ----------------------
@app.get("/inventory", response_model=InventoryOut)
def list_inventory(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
            Consulte l'inventaire des produits que le café a en stock.
            """
    inventory_items = (
        db.query(models.Inventory)
        .filter(models.Inventory.user_id == current_user.id)
        .all()
    )

    items = []

    for inv in inventory_items:
        items.append(
            InventoryItemPlayerOut(
                menu_item_id=inv.menu_item_id,
                product_name=inv.menu_item.name,
                quantity=inv.quantity
            )
        )

    return InventoryOut(items=items)


@app.get("/inventory/{item_id}", response_model=InventoryItemOut)
def read_inventory(item_id: int,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)
):
    """Récupère un item d'inventaire par son ID."""
    item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id,
        models.Inventory.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/inventory/{item_id}")
def admin_delete_inventory(
        item_id: int,
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)
):
    """Supprime n'importe quel item d'inventaire (admin uniquement)."""

    db_item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    user = db.query(models.User).filter(
        models.User.id == db_item.user_id
    ).first()

    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == db_item.menu_item_id
    ).first()

    db.delete(db_item)
    db.commit()

    return {
        "message": "Inventory deleted",
        "deleted_item": {
            "id": item_id,
            "product_name": menu_item.name if menu_item else "Unknown",
            "quantity": db_item.quantity,
            "owner": user.username if user else "Unknown"
        }
    }

# ----------------------
# CRUD COMMANDES CLIENTS
# ----------------------
@app.post("/order/client", response_model=OrderCreatedOut)
def order_for_client(
        order_data: OrderCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Passe une commande pour un client.
    La commande est mise en attente.
    """

    #Créer la commande globale
    order = models.Order(
        user_id=current_user.id,
        status=models.OrderStatus.PENDING
    )
    db.add(order)
    db.flush() #pour obtenir order.id sans comit

    #créer les lignes de commande
    response_items = []
    for item in order_data.items:
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == item.menu_item_id
        ).first()

        if not menu_item:
            raise HTTPException(status_code=404, detail="Item not found")

        order_item = models.OrderItem(
            order_id = order.id,
            menu_item_id= item.menu_item_id,
            quantity=item.quantity,
    )
        response_items.append(
            {"menu_item_name": menu_item.name,
             "menu_item_id": menu_item.id,
             "quantity": item.quantity
             }
        )

        db.add(order_item)

        log_action(
            db=db,
            user_id=current_user.id,
            action_type="order_created",
            message=f"Nouvelle commande : {item.quantity}x {menu_item.name}"
        )


    #comit final
    db.commit()

    return {
        "message": "Commande passée",
        "order_id": order.id,
        "items": response_items
    }

@app.get("/orders/{order_id}", response_model=OrderDetailOut)
def read_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Consulter le détail de la commande.
    """
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    # Vérification:
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")

    items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()

    items_response = []
    for item in items:
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == item.menu_item_id
        ).first()

        items_response.append(
            {"menu_item_id": menu_item.id,
             "menu_item_name": menu_item.name,
             "quantity": item.quantity}
        )

    return {
        "status" : order.status,
        "items" : items_response
    }

@app.patch("/orders/{order_id}/complete", response_model=OrderStatusOut)
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Change le statut d'une commande de PENDING à COMPLETED.
    Retire le stock, ajoute l'argent au joueur et log l'action.
    """

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    # Vérifications:
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    if order.status != models.OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order is not pending")

    order_items = (db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all())
    for item in order_items:
        inventory = db.query(models.Inventory).filter(
            models.Inventory.user_id == current_user.id,
            models.Inventory.menu_item_id == item.menu_item_id
        ).first()
        if not inventory or inventory.quantity < item.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

    #Effets
    total = Decimal("0.00")
    for item in order_items:
        inventory = db.query(models.Inventory).filter(
            models.Inventory.user_id == current_user.id,
            models.Inventory.menu_item_id == item.menu_item_id
        ).first()

        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == item.menu_item_id).first()

        montant = menu_item.selling_price * item.quantity
        total+=montant
        log_action(
            db=db,
            user_id=current_user.id,
            action_type="order_completed",
            message=f"Commande complétée : {item.quantity}x {menu_item.name} (+{montant}€)"
        )
        inventory.quantity -= item.quantity

    try:
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

@app.patch("/orders/{order_id}/cancel", response_model=OrderStatusOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Change le statut d'une commande de PENDING à CANCELLED.
    Le joueur n'a pas réussi à faire la commande à temps, la commande est annulée.
    """

    #Vérificiations
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

@app.get("/admin/orders", response_model=PaginatedAdminOrdersOut)
def list_all_orders(
    page: int = 1,
    limit: int = 20,
    status: OrderStatusEnum | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    """Liste toutes les commandes de tous les joueurs (admin uniquement)."""

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
# --------------------------
# ROUTES POUR LES STATISTIQUES DU JEU
# --------------------------

@app.get("/admin/stats")
def get_global_stats(
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)  #Admin requis
):
    """Statistiques globales du jeu (admin uniquement)."""

    # Compter les utilisateurs
    total_users = db.query(models.User).count()
    total_admins = db.query(models.User).filter(models.User.is_admin == True).count()

    # Compter les produits
    total_menu_items = db.query(models.MenuItem).count()

    # Compter les commandes
    total_orders = db.query(models.Order).count()

    # Argent total en circulation
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

@app.get("/game/history")
def get_game_history(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Récupère l'historique complet des actions du joueur."""

    logs = db.query(models.GameLog).filter(
        models.GameLog.user_id == current_user.id
    ).order_by(
        models.GameLog.timestamp.desc()  # Plus récent en premier
    ).all()

    return {
        "player": {
            "username": current_user.username,
            "money": current_user.money
        },
        "total_actions": len(logs),
        "history": logs
    }


@app.get("/game/stats")
def get_game_stats(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques cumulatives du joueur."""

    # Récupérer ou créer PlayerProgress
    progress = db.query(models.PlayerProgress).filter(
        models.PlayerProgress.user_id == current_user.id
    ).first()

    if not progress:
        # Si le joueur n'a pas encore de stats, en créer
        progress = models.PlayerProgress(user_id=current_user.id)
        db.add(progress)
        db.commit()
        db.refresh(progress)

    # Calculer le profit net
    profit = progress.total_money_earned - progress.total_money_spent

    return {
        "player": {
            "username": current_user.username,
            "current_money": current_user.money,
            "level": progress.current_level
        },
        "stats": {
            "total_money_earned": progress.total_money_earned,
            "total_money_spent": progress.total_money_spent,
            "profit": profit,
            "total_orders": progress.total_orders
        }
    }

# ==========================================
# ROUTES INTERFACE WEB
# ==========================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    """Page d'accueil."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse, include_in_schema=False)
async def signup_page(request: Request):
    """Page d'inscription."""
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse, include_in_schema=False)
async def signup_form(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        money: Decimal = Form(Decimal("1000.00")),
        db: Session = Depends(get_db)
):
    """Traiter le formulaire d'inscription."""
    existing_user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Ce nom d'utilisateur existe déjà"}
        )

    hashed = hash_password(password)
    db_user = models.User(
        username=username,
        password_hash=hashed,
        money=money,
        is_admin=False
    )

    db.add(db_user)
    db.commit()

    return RedirectResponse(url="/login?success=1", status_code=303)


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request, success: int = 0):
    """Page de connexion."""
    success_msg = "Compte créé avec succès ! Vous pouvez vous connecter." if success else None
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "success": success_msg}
    )


@app.post("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_form(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """Traiter le formulaire de connexion."""
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Nom d'utilisateur ou mot de passe incorrect"}
        )

    access_token = create_access_token(data={"user_id": user.id})

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Page dashboard du joueur."""
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        payload = decode_access_token(token)
        user_id = payload["user_id"]

        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            return RedirectResponse(url="/login", status_code=303)

        progress = db.query(models.PlayerProgress).filter(
            models.PlayerProgress.user_id == user.id
        ).first()

        if not progress:
            progress = models.PlayerProgress(
                user_id=user.id,
                total_money_earned=Decimal("0.00"),
                total_orders=0,
                current_level=1,
                total_money_spent=Decimal("0.00")
            )
            db.add(progress)
            db.commit()
            db.refresh(progress)

        level_requirements = {
            1: {"money": 100, "orders": 10},
            2: {"money": 500, "orders": 50},
            3: {"money": 2000, "orders": 200},
            4: {"money": 10000, "orders": 1000},
        }

        next_level = progress.current_level + 1 if progress.current_level < 5 else 5
        next_requirements = level_requirements.get(progress.current_level, {"money": 10000, "orders": 1000})

        money_percent = min(100, (progress.total_money_earned / next_requirements["money"]) * 100)
        orders_percent = min(100, (progress.total_orders / next_requirements["orders"]) * 100)

        can_level_up = (progress.total_money_earned >= next_requirements["money"] and
                        progress.total_orders >= next_requirements["orders"])

        notifications = []

        inventory = db.query(models.Inventory).filter(
            models.Inventory.user_id == user.id,
            models.Inventory.quantity < 10
        ).all()

        for inv in inventory:
            menu_item = db.query(models.MenuItem).filter(
                models.MenuItem.id == inv.menu_item_id
            ).first()
            if menu_item:
                notifications.append({
                    "type": "warning",
                    "message": f" Stock faible : {menu_item.name} ({inv.quantity} unités)"
                })

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "player": {
                "username": user.username,
                "money": round(user.money, 2),
                "level": progress.current_level
            },
            "progress": {
                "earned": round(progress.total_money_earned, 2),
                "orders": progress.total_orders,
                "next_level_money": next_requirements["money"],
                "next_level_orders": next_requirements["orders"],
                "money_percent": round(money_percent, 2),
                "orders_percent": round(orders_percent, 2),
                "can_level_up": can_level_up
            },
            "notifications": notifications
        })

    except Exception as e:
        print(f"Erreur dashboard: {e}")
        return RedirectResponse(url="/login", status_code=303)


@app.get("/logout", include_in_schema=False)
async def logout():
    """Déconnexion."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@app.get("/stock", response_class=HTMLResponse, include_in_schema=False)
async def stock(request: Request, db: Session = Depends(get_db)):
    """Page de gestion du stock."""
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        # Décoder le token
        payload = decode_access_token(token)
        user_id = payload["user_id"]

        # Récupérer le user
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            return RedirectResponse(url="/login", status_code=303)

        # Récupérer l'inventaire
        inventory = db.query(models.Inventory).filter(
            models.Inventory.user_id == user.id
        ).all()

        # Enrichir avec les détails du menu
        stock_items = []
        for inv in inventory:
            menu_item = db.query(models.MenuItem).filter(
                models.MenuItem.id == inv.menu_item_id
            ).first()

            if menu_item:
                stock_items.append({
                    "id": inv.id,
                    "menu_item_id": inv.menu_item_id,
                    "name": menu_item.name,
                    "quantity": inv.quantity,
                    "status": "low" if inv.quantity < 10 else "ok"
                })

        return templates.TemplateResponse("stock.html", {
            "request": request,
            "player": {
                "username": user.username,
                "money": round(user.money, 2)
            },
            "stock_items": stock_items
        })

    except Exception as e:
        print(f"Erreur stock: {e}")
        return RedirectResponse(url="/login", status_code=303)


@app.get("/stats", response_class=HTMLResponse, include_in_schema=False)
async def stats(request: Request, db: Session = Depends(get_db)):
    """Page stats"""
    token = request.cookies.get("access_token")

    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        # Décoder le token
        payload = decode_access_token(token)
        user_id = payload["user_id"]

        # Récupérer le user
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            return RedirectResponse(url="/login", status_code=303)

        # Récupérer les stats
        progress = db.query(models.PlayerProgress).filter(
            models.PlayerProgress.user_id == user.id
        ).first()

        if not progress:
            progress = models.PlayerProgress(
                user_id=user.id,
                total_money_earned=Decimal("0.00"),
                total_orders=0,
                current_level=1,
                total_money_spent=Decimal("0.00")
            )
            db.add(progress)
            db.commit()
            db.refresh(progress)

        # Calculer le profit
        profit = progress.total_money_earned - progress.total_money_spent

        return templates.TemplateResponse("stats.html", {
            "request": request,
            "player": {
                "username": user.username,
                "money": round(user.money, 2),
                "level": progress.current_level
            },
            "stats": {
                "total_earned": round(progress.total_money_earned, 2),
                "total_spent": round(progress.total_money_spent, 2),
                "profit": round(profit, 2),
                "total_orders": progress.total_orders
            }
        })

    except Exception as e:
        print(f"Erreur stats: {e}")
        return RedirectResponse(url="/login", status_code=303)