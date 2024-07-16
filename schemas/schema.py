from typing import Optional
from pydantic import BaseModel

# ESQUEMA PARA TABELA USUARIO 
class UserBase(BaseModel):
    name: str
    email: str
    password: str

class UserCreate(UserBase):
    role: str  # 'cliente', 'agente_imobiliario', 'intermediario_bancario', 'parceiro_turistico'

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
