from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from enum import Enum as PyEnum


# ----------------
# UTILISATEUR
# ------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    money = Column(Float, default=0.0)
    is_admin = Column(Boolean, default=False)

    # Relations
    orders = relationship("Order", back_populates="user")
    inventory_items = relationship("Inventory", back_populates="user")
    game_logs = relationship("GameLog", back_populates="user")
    player_progress = relationship("PlayerProgress", back_populates="user", uselist=False)


# ----------------
# MENU
# ------------------------
class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)

    inventory_items = relationship("Inventory", back_populates="menu_item")
    orders_items = relationship("OrderItem", back_populates="menu_item")


# ----------------
# Inventaire
# ------------------------
class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relations
    user = relationship("User", back_populates="inventory_items")
    menu_item = relationship("MenuItem", back_populates="inventory_items")


# ----------------
# Commandes
# ------------------------
class OrderStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True) # Les numéros de commandes
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING,  nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)

    # Relations
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")

# ----------------
# GameLog : Pour l'historique du joueur
# ------------------------
class GameLog(Base):
    __tablename__ = "gamelog"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String)
    message = Column(String)
    amount = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relation
    user = relationship("User", back_populates="game_logs")


# ----------------
# PlayerProgress : Pour les stats cumulatives des joueurs
# ----------------------
class PlayerProgress(Base):
    __tablename__ = "player_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_money_earned = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    total_money_spent = Column(Float, default=0.0)

    # Relation
    user = relationship("User", back_populates="player_progress")