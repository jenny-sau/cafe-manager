from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from database import Base

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
