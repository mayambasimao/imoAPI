from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# ESQUEMA PARA TABELA USUARIO 
class UserBase(BaseModel):
    name: str
    email: str
    password: str

class UserCreate(UserBase):
    role: str  # 'cliente', 'agente_imobiliario', 'intermediario_bancario', 'parceiro_turistico', 'vendedor'

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True


# ESQUEMA PARA TABELA HOUSES
class HouseBase(BaseModel):
    title: str
    description: str
    price: float
    type_transaction: str

class HouseCreate(HouseBase):
    agent_id: Optional[int]

class HouseUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[float]
    type_transaction: Optional[str]
    status: Optional[bool]

class House(HouseBase):
    id: int
    seller_id: int
    agent_id: Optional[int]
    status: bool
    assignment_status: str

    class Config:
        orm_mode = True

#eESQUEMA PARA TABELA VISITA
class VisitRequest(BaseModel):
    house_id: int
    scheduled_time: datetime

class VisitRequestCreate(VisitRequest):
    pass

class VisitRequestt(VisitRequest):
    id: int
    client_id: int
    agent_id: int
    status: str   

    class Config:
        orm_mode = True

# ESQUEMA PARA SHORT RENTALS
class ShortRentalBase(BaseModel):
    house_id: int
    start_date: datetime
    end_date: datetime

class ShortRentalCreate(ShortRentalBase):
    pass

class ShortRental(ShortRentalBase):
    id: int
    client_id: int
    agent_id: int
    status: str

    class Config:
        orm_mode = True       

class TokenData(BaseModel):
    access_token: str
    token_type: str
    name: str
    role: str