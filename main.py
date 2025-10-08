from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, UserOut
from database import Base, engine, get_db
import models

# Crée la DB dès le lancement
Base.metadata.create_all(bind=engine)

# Crée l'application FastAP
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
