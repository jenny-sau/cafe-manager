from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from schemas import (
    UserCreate, UserOut,
    MenuItemCreate, MenuItemOut,
    InventoryCreate, InventoryOut, InventoryUpdate,
    OrderCreate, OrderRead,
    UserSignup, UserResponse, UserLogin
)
from database import Base, engine, get_db
import models
from auth import hash_password, verify_password, create_access_token, decode_access_token

# ----------------------
# CRÉATION DE LA BASE DE DONNÉES
# ----------------------
Base.metadata.create_all(bind=engine)

# ----------------------
# INITIALISATION DE L'APPLICATION FASTAPI
# ----------------------
app = FastAPI()

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


# ----------------------
# ROUTES SIMPLES / TEST
# ----------------------
@app.get("/")
async def root():
    """Page d'accueil simple."""
    return {"message": "Welcome to cafe manager"}


@app.get("/health")
async def health():
    """Vérifie que l'application fonctionne."""
    return {"status": "ok"}


# ----------------------
# CRUD UTILISATEURS
# ----------------------
@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur."""
    db_user = models.User(username=user.username, money=user.money)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Récupère un utilisateur par son ID."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """Modifie un utilisateur existant."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.money = user.money
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Supprime un utilisateur."""
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
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    """Crée un nouvel item du menu."""
    db_menu_item = models.MenuItem(name=item.name, price=item.price)
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@app.get("/menu/{menu_id}", response_model=MenuItemOut)
def read_menu_item(menu_id: int, db: Session = Depends(get_db)):
    """Récupère un item du menu par son ID."""
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item


@app.get("/menu", response_model=list[MenuItemOut])
def list_menu(db: Session = Depends(get_db)):
    """Liste tous les items du menu."""
    return db.query(models.MenuItem).all()


@app.put("/menu/{menu_id}", response_model=MenuItemOut)
def update_menu_item(menu_id: int, menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    """Modifie un item du menu existant."""
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db_menu_item.name = menu_item.name
    db_menu_item.price = menu_item.price
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@app.delete("/menu/{menu_id}")
def delete_menu_item(menu_id: int, db: Session = Depends(get_db)):
    """Supprime un item du menu."""
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(db_menu_item)
    db.commit()
    return {"message": "Menu item deleted"}


# ----------------------
# CRUD INVENTAIRE (PROTÉGÉ)
# ----------------------
@app.post("/inventory", response_model=InventoryOut)
def create_inventory(
        inventory: InventoryCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """Crée un nouvel inventaire (nécessite authentification)."""
    db_inventory = models.Inventory(
        menu_item_id=inventory.menu_item_id,
        quantity=inventory.quantity
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@app.get("/inventory", response_model=list[InventoryOut])
def list_inventory(db: Session = Depends(get_db)):
    """Liste tous les items d'inventaire."""
    return db.query(models.Inventory).all()


@app.get("/inventory/{item_id}", response_model=InventoryOut)
def read_inventory(item_id: int, db: Session = Depends(get_db)):
    """Récupère un item d'inventaire par son ID."""
    item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/inventory/{item_id}", response_model=InventoryOut)
def update_inventory(item_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db)):
    """Met à jour la quantité d'un item d'inventaire."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.quantity = inventory.quantity
    db.commit()
    db.refresh(db_item)
    return db_item


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
@app.post("/order/client", response_model=OrderRead)
def order_for_client(
        order: OrderCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Passe une commande pour un client (nécessite authentification).
    Diminue le stock si la quantité est disponible.
    """
    # Cherche l'inventory par menu_item_id
    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.menu_item_id == order.menu_item_id
    ).first()

    if not inventory_item or inventory_item.quantity < order.quantity:
        raise HTTPException(status_code=400, detail="Stock insuffisant")

    # Retirer du stock
    inventory_item.quantity -= order.quantity

    # Créer la commande
    db_order = models.Order(menu_item_id=order.menu_item_id, quantity=order.quantity)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


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
    Permet au joueur de réapprovisionner le stock (nécessite authentification).
    Si l'item n'existe pas, il est créé.
    Sinon, la quantité existante est augmentée.
    """
    inventory_item = db.query(models.Inventory).filter(
        models.Inventory.menu_item_id == order.menu_item_id
    ).first()

    if not inventory_item:
        # Crée un nouvel item dans l'inventaire
        inventory_item = models.Inventory(
            menu_item_id=order.menu_item_id,
            quantity=order.quantity
        )
        db.add(inventory_item)
    else:
        # Ajoute à la quantité existante
        inventory_item.quantity += order.quantity

    db.commit()
    db.refresh(inventory_item)
    return inventory_item


# --------------------------
# AUTHENTIFICATION
# --------------------------
@app.post("/auth/signup", response_model=UserResponse)
def signup(user: UserSignup, db: Session = Depends(get_db)):
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
        money=user.money
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