from fastapi import FastAPI
from schemas import UserCreate, UserOut
from database import Base, engine
import models

app = FastAPI()

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to cafe manager"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate):
    return {"id": 1, "username": user.username, "money": user.money}

# Crée la DB au démarrage du serveur
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
