from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

# --------------------------
# UTILISATEUR
# --------------------------
class UserCreate(BaseModel):
    """Données pour créer un utilisateur."""
    username: str
    money: float = 0.0


class UserOut(BaseModel):
    """Utilisateur retourné par l’API."""
    id: int
    username: str
    money: float
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    username: Optional[str] = None
    money: Optional[int] = None


# --------------------------
# MENU ITEMS
# --------------------------
class MenuItemCreate(BaseModel):
    name: str
    purchase_price: float
    selling_price: float

    @field_validator('purchase_price', 'selling_price')
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Le prix doit être supérieur à 0')
        return v


class MenuItemOut(BaseModel):
    id: int
    name: str
    purchase_price: float
    selling_price: float
    model_config = {"from_attributes": True}

class MenuItemWithStock(BaseModel):
    id: int
    name: str
    purchase_price: float
    selling_price: float
    stock: int
    available: str

class MenuListResponse(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    items: list[MenuItemWithStock]

class MenuItemUpdate(BaseModel):
    name: Optional[str]= None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
# --------------------------
# INVENTAIRE
# --------------------------
class InventoryCreate(BaseModel):
    """Création d’un item dans l’inventaire."""
    menu_item_id: int
    quantity: int

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('La quantité ne peut pas être négative')
        return v


class InventoryOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    model_config = {"from_attributes": True}


class InventoryUpdate(BaseModel):
    """Mise à jour de la quantité d’un item d’inventaire."""
    quantity: int

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('La quantité ne peut pas être négative')
        return v


# --------------------------
# COMMANDES
# --------------------------
class OrderCreate(BaseModel):
    """Commande client ou réapprovisionnement joueur."""
    menu_item_id: int
    quantity: int

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('La quantité doit être supérieure à 0')
        return v


class OrderRead(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    model_config = {"from_attributes": True}


# --------------------------
# AUTHENTIFICATION
# --------------------------
class UserSignup(BaseModel):
    """Données pour créer un compte."""
    username: str
    password: str
    money: float = 0.0
    is_admin: bool = False

    @field_validator('username')
    @classmethod
    def username_not_empty(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Username doit faire au moins 3 caractères')
        return v

    @field_validator('password')
    @classmethod
    def password_strong_enough(cls, v):
        if len(v) < 6:
            raise ValueError('Password doit faire au moins 6 caractères')
        return v


class UserResponse(BaseModel):
    """Utilisateur retourné après signup/login (SANS password)."""
    id: int
    username: str
    money: float
    is_admin: bool
    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    """Données pour se connecter."""
    username: str
    password: str

# --------------------------
# HISTORIQUE DU JOUEUR
# --------------------------
class GameLogOut(BaseModel):
    id: int
    action_type: str
    message: str
    amount: float | None  # ← Peut être None
    timestamp: datetime
    model_config = {"from_attributes": True}

# --------------------------
# STATISTIQUES DU JOUEUR
# --------------------------
class PlayerProgressOut(BaseModel):
    id: int
    user_id: int
    total_money_earned: float
    total_orders: int
    current_level: int
    total_money_spent: float
    model_config = {"from_attributes": True}