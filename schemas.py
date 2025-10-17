from pydantic import BaseModel, validator
class UserCreate(BaseModel):  # Ce que le client envoie
    username: str
    money: float = 0.0

class UserOut(BaseModel):     # Ce que l'API renvoie
    id: int
    username: str
    money: float

class MenuItemCreate(BaseModel):
    name: str
    price: float

    model_config = {"from_attributes": True}

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Le prix doit être positif')
        return v

class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float

    model_config = {"from_attributes": True}

class InventoryCreate(BaseModel):
    menu_item_id: int
    quantity: int

class InventoryOut(BaseModel):
    id: int
    menu_item_id: int
    quantity: int

    model_config = {"from_attributes": True}

class InventoryUpdate(BaseModel):
    quantity: int