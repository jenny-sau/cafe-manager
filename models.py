from sqlalchemy import (
    Column, Integer, String, Numeric,
    ForeignKey, Boolean, DateTime, Enum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum


# ----------------
# USER
# ------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    money = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    is_admin = Column(Boolean, server_default="false", nullable=False)

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
    purchase_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)

    inventory_items = relationship("Inventory", back_populates="menu_item")
    orders_items = relationship("OrderItem", back_populates="menu_item")


# ----------------
# INVENTORY
# ------------------------
class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship
    user = relationship("User", back_populates="inventory_items")
    menu_item = relationship("MenuItem", back_populates="inventory_items")


# ----------------
# ORDERS
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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
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
# GameLog : For the player's history
# ------------------------
class GameLog(Base):
    __tablename__ = "gamelog"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String)
    message = Column(String)
    amount = Column(Numeric(10, 2), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    user = relationship("User", back_populates="game_logs")


# ----------------
# PlayerProgress : For players' cumulative statistics
# ----------------------
class PlayerProgress(Base):
    __tablename__ = "player_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_money_earned = Column(Numeric(12, 2), server_default="0.00")
    total_orders = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    total_money_spent = Column(Numeric(12, 2), server_default="0.00")

    # Relationship
    user = relationship("User", back_populates="player_progress")