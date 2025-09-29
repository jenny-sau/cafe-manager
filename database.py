from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de connexion à la base SQLite (fichier local "cafe.db")
SQLALCHEMY_DATABASE_URL = "sqlite:///./cafe.db"

# Création du moteur (engine) qui gère la connexion à SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session = l’outil qui permet de dialoguer avec la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = classe mère pour tous tes futurs modèles (User, MenuItem, etc.)
Base = declarative_base()
