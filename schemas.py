from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

# ------------------------------------------------------------------------------------
# AUTHENTIFICATION
# ------------------------------------------------------------------------------------

class UserSignup(BaseModel):
    """Information needed to create an account."""
    username: str
    password: str
    money: float = 0.0

    @field_validator('username')
    @classmethod
    def username_not_empty(cls, v):
        if not v or len(v) < 3:
            raise ValueError('The username must be at least 3 characters long')
        return v

    @field_validator('password')
    @classmethod
    def password_strong_enough(cls, v):
        if len(v) < 6:
            raise ValueError('The password must be at least 6 characters long')
        return v


class UserResponse(BaseModel):
    """User returned  after signup/login (WITHOUT a password)."""
    id: int
    username: str
    money: float
    is_admin: bool
    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    """Login credentials."""
    username: str
    password: str

# ------------------------------------------------------------------------------------
# USER
# ------------------------------------------------------------------------------------

class UserOut(BaseModel):
    """User data returned by the API (id, username, money). No sensitive fields exposed."""
    id: int
    username: str
    money: float
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    """Fields allowed when updating a user. All fields are optional."""
    username: Optional[str] = None
    money: Optional[float] = None

class TokenOut(BaseModel):
    """JWT token returned after a successful login."""
    access_token: str
    token_type: str = "bearer"

# ------------------------------------------------------------------------------------
# MENU ITEMS
# ------------------------------------------------------------------------------------

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

class MenuItemUpdate(BaseModel):
    name: Optional[str]= None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None

class MenuItemWithStock(BaseModel):
    """Menu item enriched with stock data from inventory. Used in paginated list."""
    id: int
    name: str
    purchase_price: float
    selling_price: float
    stock: int
    available: str

class MenuListResponse(BaseModel):
    """Paginated list of menu items with stock info."""
    page: int
    limit: int
    total_items: int
    total_pages: int
    items: list[MenuItemWithStock]

# ------------------------------------------------------------------------------------
# RESTOCK
# ------------------------------------------------------------------------------------

class RestockCreate(BaseModel):
    """Restocking by player."""
    menu_item_id: int
    quantity: int

    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('The quantity must be greater than 0.')
        return v

# ------------------------------------------------------------------------------------
# INVENTORY
# ------------------------------------------------------------------------------------

class InventoryItemOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int
    model_config = {"from_attributes": True}

class InventoryItemPlayerOut(BaseModel):
    menu_item_id: int
    product_name: str
    quantity: int

class InventoryOut(BaseModel):
    items: list[InventoryItemPlayerOut]

# ------------------------------------------------------------------------------------
# ORDERS
# ------------------------------------------------------------------------------------

class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

class OrderedItemOut(BaseModel):
    menu_item_id: int
    menu_item_name: str
    quantity: int

    model_config = {"from_attributes": True}

class OrderCreatedOut(BaseModel):
    """Response when creating a sales order"""
    message: str
    order_id: int
    items: list[OrderedItemOut]

class OrderStatusOut(BaseModel):
    """Response when order status changes"""
    message: str
    order_id: int

class OrderDetailOut(BaseModel):
    """Response when we view the details (i.e., the contents) of an order"""
    status: OrderStatusEnum
    items: list[OrderedItemOut]
    model_config = {"from_attributes": True}

class OrderSummaryOut(BaseModel):
    id: int
    status: OrderStatusEnum
    created_at: datetime

class PaginatedOrdersOut(BaseModel):
    """Paginated list of commands."""
    page: int
    limit: int
    total_items: int
    total_pages: int
    items: list[OrderSummaryOut]

class OrderAdminSummaryOut(BaseModel):
    id: int
    user_id: int
    status: OrderStatusEnum
    created_at: datetime

    model_config = {"from_attributes": True}

class PaginatedAdminOrdersOut(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    items: list[OrderAdminSummaryOut]

# ------------------------------------------------------------------------------------
# PLAYER HISTORY
# ------------------------------------------------------------------------------------

class GameLogOut(BaseModel):
    id: int
    action_type: str
    message: str
    amount: float | None  # ← Peut être None
    timestamp: datetime
    model_config = {"from_attributes": True}

class PlayerHistoryInfo(BaseModel):
    username: str
    money: float

class GameHistoryOut(BaseModel):
    player: PlayerHistoryInfo
    total_actions: int
    history: list[GameLogOut]

# ------------------------------------------------------------------------------------
# PLAYER STATISTICS
# ------------------------------------------------------------------------------------

class PlayerStatsInfo(BaseModel):
    """Basic player information for stats."""
    username: str
    current_money: float
    level: int

class PlayerStatsDetails(BaseModel):
    """Player's cumulative statistics."""
    total_money_earned: float
    total_money_spent: float
    profit: float
    total_orders: int

class PlayerStatsOut(BaseModel):
    """Complete player statistics."""
    player: PlayerStatsInfo
    stats: PlayerStatsDetails