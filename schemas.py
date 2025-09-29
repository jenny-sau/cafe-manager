from pydantic import BaseModel
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

class MenuItemOut(BaseModel):
    id: int
    name: str
    price: float

    model_config = {"from_attributes": True}