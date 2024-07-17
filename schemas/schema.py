from typing import Optional
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

# ESQUEMA PARA TABELA SERVICOS ESPECIALIZADOS
class ServicosEspecializadosBase(BaseModel):
    tipo: str
    descricao: str
    preco: int

class ServicosEspecializadosCreate(ServicosEspecializadosBase):
    pass

class ServicosEspecializados(ServicosEspecializadosBase):
    id: int
    
    class Config:
        orm_mode = True

# ESQUEMA PARA TABELA PARCEIROS TURISTICOS
class ParceiroTuristicoBase(BaseModel):
    nome_parceiro: str
    tipo_servico: str
    detalhes: str

class ParceiroTuristicoCreate(ParceiroTuristicoBase):
    pass

class ParceiroTuristico(ParceiroTuristicoBase):
    id: int
    
    class Config:
        orm_mode = True

# ESQUEMA PARA TABELA HOUSES
class HouseBase(BaseModel):
    title: str
    description: str
    price: float
    status: str
    
class HouseCreate(HouseBase):
    seller_id: int
    agent_id: Optional[int] = None

class HouseUpdate(HouseBase):
    agent_id: Optional[int] = None

class House(HouseBase):
    id: int
    seller_id: int
    agent_id: Optional[int] = None

    class Config:
        orm_mode = True
        
class TokenData(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None