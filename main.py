from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import (
    UserCreate, UserOut,
    MenuItemCreate, MenuItemOut,
    InventoryCreate, InventoryOut, InventoryUpdate,
    OrderCreate, OrderRead
)
from database import Base, engine, get_db
import models

# ----------------------
# CRÉATION DE LA BASE DE DONNÉES
# ----------------------
Base.metadata.create_all(bind=engine)

# ----------------------
# INITIALISATION DE L'APPLICATION FASTAPI
# ----------------------
app = FastAPI()

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
# CRUD INVENTAIRE
# ----------------------
@app.post("/inventory", response_model=InventoryOut)
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    """Crée un nouvel inventaire."""
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
# COMMANDES CLIENTS (diminue stock)
# ----------------------
@app.post("/order/client", response_model=OrderRead)
def order_for_client(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Passe une commande pour un client.
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
# RÉAPPROVISIONNEMENT PAR LE JOUEUR (augmente stock)
# ----------------------
@app.post("/order/restock", response_model=InventoryOut)
def restock_item(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Permet au joueur de réapprovisionner le stock.
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