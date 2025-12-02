from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from database import Base
from datetime import datetime

# --------------------------
# UTILISATEUR
# --------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    money = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)
# --------------------------
# MENU
# --------------------------
class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)


# --------------------------
# Inventaire
# --------------------------
class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))

# --------------------------
# Commandes
# --------------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

# --------------------------
# GameLog -> Pour l'historique du joueur
# --------------------------
class GameLog (Base):
    __tablename__ ="gameLog"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String)
    message = Column(String) # Exemple : "Commande client : 2 cafés → +6€"
    amount = Column(Float, nullable=True) #L'argent impliqué dans l'action (peut être NULL)
    timestamp = Column(DateTime, default=datetime.utcnow)


# --------------------------
# PlayerProgress -> Pour les stats cumulatives des joueurs
# --------------------------
class PlayerProgress(Base):
    __tablename__ = "player_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_money_earned = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    total_money_spent = Column(Float, default=0.0)

