import math
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas import (
    UserCreate, UserOut, UserUpdate,
    MenuItemCreate, MenuItemOut, MenuListResponse, MenuItemWithStock, MenuItemUpdate,
    InventoryCreate, InventoryOut, InventoryUpdate,
    OrderCreate, OrderRead,
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
from game_utils import log_action

# ----------------------
# CRÉATION DE LA BASE DE DONNÉES
# ----------------------
Base.metadata.create_all(bind=engine)

# ----------------------
# INITIALISATION DE L'APPLICATION FASTAPI
# ----------------------
app = FastAPI()

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


# ----------------------
# CRUD UTILISATEURS
# ----------------------
@app.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int,
              db: Session = Depends(get_db),
              admin: models.User = Depends(get_current_admin)
):
    """Récupère un utilisateur par son ID (admin uniquement)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


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
def delete_user(user_id: int,
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
@app.post("/menu", response_model=MenuItemOut)
def create_menu_item(item: MenuItemCreate,
                     db: Session = Depends(get_db),
                     admin: models.User = Depends(get_current_admin)
):
    """Crée un nouvel item du menu (admin uniquement)."""
    db_menu_item = models.MenuItem(name=item.name, purchase_price=item.purchase_price, selling_price= item.selling_price)
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@app.get("/menu/{menu_id}", response_model=MenuItemOut)
def read_menu_item(menu_id: int,
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
    """Liste tous les items du menu avec pagination."""
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
def update_menu_item(menu_id: int,
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
def delete_menu_item(menu_id: int,
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
# CRUD INVENTAIRE (PROTÉGÉ)
# ----------------------
@app.get("/inventory")
def list_inventory(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Liste l'inventaire du joueur connecté avec détails."""

    # 1. Récupère l'inventaire du joueur
    inventory_items = db.query(models.Inventory).filter(
        models.Inventory.user_id == current_user.id
    ).all()

    # 2. Enrichis chaque item
    inventory_details = []
    notifications = []
    for inv in inventory_items:
        # Récupère le menu_item correspondant
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == inv.menu_item_id
        ).first()

        if menu_item is None:
            continue

        # Détermine le statut
        status = "low_stock" if inv.quantity < 10 else "ok"

        # Crée le dictionnaire
        product_info = {
            "id": inv.id,
            "menu_item_id": inv.menu_item_id,
            "product_name": menu_item.name if menu_item else "Unknown",
            "quantity": inv.quantity,
            "status": status
        }

        # Ajoute à la liste
        inventory_details.append(product_info)

        if inv.quantity < 10:
            notifications.append(f"⚠️ Stock faible : {menu_item.name} ({inv.quantity} unités)")
    # 3. Retourne tout
    return {
        "player": {
            "username": current_user.username,
            "money": current_user.money
        },
        "inventory": {
            "total_items": len(inventory_details),
            "items": inventory_details
        },
        "notifications": notifications

    }

@app.get("/inventory/{item_id}", response_model=InventoryOut)
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
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    """Supprime un item d'inventaire."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Inventory deleted"}


# ----------------------
# COMMANDES CLIENTS (PROTÉGÉ)
# ----------------------
@app.post("/order/client")
def order_for_client(
        order: OrderCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Passe une commande pour un client (nécessite authentification).
    Diminue le stock si la quantité est disponible.
    Ajoute l'argent au joueur et log l'action.
    """
    # 1. Chercher l'inventory par menu_item_id ET user_id
    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.menu_item_id == order.menu_item_id,
        models.Inventory.user_id == current_user.id
    ).first()

    # 2. Vérifier le stock
    if not inventory_item or inventory_item.quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Stock insuffisant")

    # 3. Récupérer le menu_item pour le nom et le prix
    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == order.menu_item_id
    ).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # 4. Retirer du stock
    inventory_item.quantity -= order.quantity

    # 5. Créer la commande
    db_order = models.Order(
        menu_item_id=order.menu_item_id,
        quantity=order.quantity,
        user_id=current_user.id
    )
    db.add(db_order)

    # 6. Calculer et ajouter l'argent au joueur
    montant_gagne = menu_item.selling_price * order.quantity
    current_user.money += montant_gagne

    # 7. Logger l'action
    log_action(
        db=db,
        user_id=current_user.id,
        action_type="order_client",
        message=f"Vente : {order.quantity}x {menu_item.name} → +{montant_gagne}€",
        amount=montant_gagne
    )

    # 8. Sauvegarder TOUT en une fois (stock + commande + argent + log)
    db.commit()
    db.refresh(db_order)

    return {
        "order": {
            "id": db_order.id,
            "menu_item_id": db_order.menu_item_id,
            "quantity": db_order.quantity,
            "user_id": db_order.user_id
        },
        "message": f"Vente : {order.quantity}x {menu_item.name} → +{montant_gagne:.2f}€ | Stock restant : {inventory_item.quantity} | Argent : {current_user.money:.2f}€"
    }

@app.post("/orders/{order_id}/complete")
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")

    if order.status != models.OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Order is not pending")

    inventory = db.query(models.Inventory).filter(
        models.Inventory.user_id == current_user.id,
        models.Inventory.menu_item_id == order.menu_item_id
    ).first()

    if not inventory:
        raise HTTPException(status_code=400, detail="No inventory for this item")

    if inventory.quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == order.menu_item_id
    ).first()

    try:
        order.status = models.OrderStatus.COMPLETED
        inventory.quantity -= order.quantity
        current_user.money += menu_item.selling_price * order.quantity

        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Order processing failed")

    return {
        "message": "Order completed",
        "order_id": order.id,
        "new_balance": current_user.money
    }



# ----------------------
# RÉAPPROVISIONNEMENT PAR LE JOUEUR (PROTÉGÉ)
# ----------------------
@app.post("/order/restock", response_model=InventoryOut)
def restock_item(
        order: OrderCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
        Passe une commande pour le café (nécessite authentification).
        Augmente le stock si la quantité est disponible.
        Diminue l'argent au joueur et log l'action.
        """
    # 1. Récupérer le menu_item pour avoir le prix
    menu_item = db.query(models.MenuItem).filter(
        models.MenuItem.id == order.menu_item_id
    ).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    # 2. Calculer le coût
    montant_depense = menu_item.purchase_price * order.quantity

    # 3. Vérifier que le joueur a assez d'argent
    if current_user.money < montant_depense:
        raise HTTPException(status_code=400, detail="Pas assez d'argent !")

    # 4. Déduire l'argent
    current_user.money -= montant_depense

    # 5. Ajouter/mettre à jour l'inventaire (ton code existant)
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

    # 6. Logger l'action
    log_action(
        db=db,
        user_id=current_user.id,
        action_type="restock",
        message=f"Réapprovisionnement : {order.quantity}x {menu_item.name} → -{montant_depense}€",
        amount=-montant_depense
    )

    # 7. Sauvegarder TOUT (inventaire + argent user + log)
    db.commit()
    db.refresh(inventory_item)

    return inventory_item

@app.get("/orders")
def list_orders(
        page: int = 1,
        limit: int = 20,
        menu_item_id: int = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Liste toutes les commandes du joueur avec pagination."""

    skip = (page - 1) * limit
    query = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    )
    #Filtre optionnel
    if menu_item_id is not None:
        query = query.filter(models.Order.menu_item_id == menu_item_id)

    orders = query.order_by(
        models.Order.id.desc()
    ).offset(skip).limit(limit).all()

    count_query = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    )
    if menu_item_id is not None:
        count_query = count_query.filter(models.Order.menu_item_id == menu_item_id)

    total_items = count_query.count()

    total_pages = math.ceil(total_items / limit)

    orders_details = []
    for order in orders:
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == order.menu_item_id
        ).first()

        orders_details.append({
            "id": order.id,
            "menu_item_id": order.menu_item_id,
            "product_name": menu_item.name if menu_item else "Unknown",
            "quantity": order.quantity
        })

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "orders": orders_details
    }

# --------------------------
# AUTHENTIFICATION
# --------------------------
@app.post("/auth/signup", response_model=UserResponse)
@limiter.limit("5/minute") # ← Maximum 5 signups par minute
def signup(request: Request, user: UserSignup, db: Session = Depends(get_db)):
    """Créer un nouveau compte utilisateur."""
    # 1. Chercher si username existe déjà
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    # 2. Si existe, erreur
    if existing_user:
        raise HTTPException(status_code=400, detail="Username déjà pris")

    # 3. Hasher le password
    hashed = hash_password(user.password)

    # 4. Créer le user
    db_user = models.User(
        username=user.username,
        password_hash=hashed,
        money=user.money,
        is_admin = user.is_admin
    )

    # 5. Sauvegarder
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 6. Retourner (sans password)
    return db_user


@app.post("/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Se connecter et recevoir un JWT token."""
    # 1. Trouver le user par username
    user = db.query(models.User).filter(
        models.User.username == credentials.username
    ).first()

    # 2. Si user n'existe pas
    if not user:
        raise HTTPException(status_code=401, detail="Username ou password incorrect")

    # 3. Vérifier le password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username ou password incorrect")

    # 4. Créer le JWT avec l'id du user
    access_token = create_access_token(data={"user_id": user.id})

    # 5. Retourner le token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "money": user.money
        }
    }


# --------------------------
# ROUTES ADMIN
# --------------------------
@app.get("/admin/users")
def list_all_users(
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)  # ← Admin requis
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



@app.get("/admin/orders")
def list_all_orders(
        page: int = 1,
        limit: int = 20,
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)  # ← Admin requis
):
    """Liste toutes les commandes de tous les joueurs (admin uniquement)."""

    skip = (page - 1) * limit

    # Toutes les commandes (pas de filtre user_id)
    orders = db.query(models.Order).order_by(
        models.Order.id.desc()
    ).offset(skip).limit(limit).all()

    total_items = db.query(models.Order).count()
    total_pages = math.ceil(total_items / limit)

    orders_details = []
    for order in orders:
        # Récupérer le menu_item
        menu_item = db.query(models.MenuItem).filter(
            models.MenuItem.id == order.menu_item_id
        ).first()

        # Récupérer l'utilisateur qui a passé la commande
        user = db.query(models.User).filter(
            models.User.id == order.user_id
        ).first()

        orders_details.append({
            "id": order.id,
            "menu_item_id": order.menu_item_id,
            "product_name": menu_item.name if menu_item else "Unknown",
            "quantity": order.quantity,
            "user_id": order.user_id,
            "username": user.username if user else "Unknown"
        })

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "orders": orders_details
    }


@app.delete("/admin/inventory/{item_id}")
def admin_delete_inventory(
        item_id: int,
        db: Session = Depends(get_db),
        current_admin: models.User = Depends(get_current_admin)  # ← Admin requis
):
    """Supprime n'importe quel item d'inventaire (admin uniquement)."""

    # Pas de filtre user_id, on peut supprimer n'importe quel inventaire
    db_item = db.query(models.Inventory).filter(
        models.Inventory.id == item_id
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Récupérer les infos avant de supprimer
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


# --------------------------
# ROUTES POUR HISTORIQUE DU JOUEUR
# --------------------------
@app.get("/game/history")
def get_game_history(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Récupère l'historique complet des actions du joueur."""

    # 1. Récupérer tous les logs du joueur
    logs = db.query(models.GameLog).filter(
        models.GameLog.user_id == current_user.id
    ).order_by(
        models.GameLog.timestamp.desc()  # Plus récent en premier
    ).all()

    # 2. Retourner
    return {
        "player": {
            "username": current_user.username,
            "money": current_user.money
        },
        "total_actions": len(logs),
        "history": logs
    }


# --------------------------
# ROUTES POUR STATISTIQUES DU JOUEUR
# --------------------------

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
        money: float = Form(1000),
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
                total_money_earned=0.0,
                total_orders=0,
                current_level=1,
                total_money_spent=0.0
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
                total_money_earned=0.0,
                total_orders=0,
                current_level=1,
                total_money_spent=0.0
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