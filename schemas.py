from pydantic import BaseModel, field_validator

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


# --------------------------
# MENU ITEMS
# --------------------------
class MenuItemCreate(BaseModel):
    """Création d’un produit du menu."""
    name: str
    price: float

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Le prix doit être supérieur à 0')
        return v


class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float
    model_config = {"from_attributes": True}


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
