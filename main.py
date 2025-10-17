from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, UserOut, MenuItemCreate, MenuItemOut, InventoryCreate, InventoryOut, InventoryUpdate
from database import Base, engine, get_db
import models

# Crée la DB dès le lancement
Base.metadata.create_all(bind=engine)

# Crée l'application FastAPI
app = FastAPI()

# Routes simples
@app.get("/")
async def root():
    return {"message": "Welcome to cafe manager"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# 4️⃣ CRUD Users - POST /users
@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crée un utilisateur et le sauvegarde en base.
    """
    # Créer un objet User à partir du schéma Pydantic
    db_user = models.User(username=user.username, money=user.money)

    # Ajouter l'objet à la session
    db.add(db_user)

    # Sauvegarder en base
    db.commit()

    # Rafraîchir l'objet pour récupérer son id auto-incrémenté
    db.refresh(db_user)

    return db_user

# CRUD Users - GET /users/{id}
@app.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """
    Modifie un utilisateur existant.
    """
    # Chercher l'utilisateur dans la base
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    # Si pas trouvé, erreur 404
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Modifier les champs
    db_user.username = user.username
    db_user.money = user.money

    # Sauvegarder les modifications
    db.commit()

    # Rafraîchir l'objet
    db.refresh(db_user)

    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Supprime un utilisateur.
    """
    # Chercher l'utilisateur dans la base
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    # Si pas trouvé, erreur 404
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Supprimer l'objet
    db.delete(db_user)

    # Sauvegarder la suppression
    db.commit()

    return {"message": "User deleted"}

@app.post("/menu",response_model=MenuItemOut)
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):

    # # Créer un objet MenuItem à partir du schéma Pydantic
    db_menu_item = models.MenuItem(name=item.name, price=item.price)

    # Ajouter l'objet à la session
    db.add(db_menu_item)

    # Sauvegarder en base
    db.commit()

    # Rafraîchir l'objet pour récupérer son id auto-incrémenté
    db.refresh(db_menu_item)

    return db_menu_item


@app.get("/menu/{menu_id}", response_model=MenuItemOut)
def read_menu_item(menu_id: int, db: Session = Depends(get_db)):
    """
    Récupère un produit menu par son id.
    """
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()

    if menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return menu_item


@app.put("/menu/{menu_id}", response_model=MenuItemOut)
def update_menu_item(menu_id: int, menu_item: MenuItemCreate, db: Session = Depends(get_db)):
    """
    Modifie un produit menu existant.
    """
    # Chercher le produit
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()

    # Vérifier s'il existe
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Modifier les champs
    db_menu_item.name = menu_item.name
    db_menu_item.price = menu_item.price

    # Sauvegarder
    db.commit()

    # Rafraîchir
    db.refresh(db_menu_item)

    return db_menu_item


@app.delete("/menu/{menu_id}")
def delete_menu_item(menu_id: int, db: Session = Depends(get_db)):
    """
    Supprime un produit menu.
    """
    db_menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == menu_id).first()

    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")

    db.delete(db_menu_item)

    db.commit()

    return {"message": "Menu item deleted"}

@app.get("/menu", response_model=list[MenuItemOut])
def list_menu(db: Session = Depends(get_db)):
    return db.query(models.MenuItem).all()

@app.post("/inventory", response_model=InventoryOut)
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    db_inventory= models.Inventory(menu_item_id=inventory.menu_item_id, quantity=inventory.quantity)
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

@app.get("/inventory/{item_id}", response_model=InventoryOut)
def read_inventory(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/inventory/{item_id}", response_model=InventoryOut)
def update_inventory(item_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db)):
    db_item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Modifier SEULEMENT la quantité
    db_item.quantity = inventory.quantity

    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/inventory/{item_id}")
def delete_inventory(item_id: int, db: Session = Depends(get_db)):
    """
    Supprime un inventaire.
    """
    db_item = db.query(models.Inventory).filter(models.Inventory.id == item_id).first()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Inventory not found")

    db.delete(db_item)
    db.commit()

    return {"message": "Inventory deleted"}


