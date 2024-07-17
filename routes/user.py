from fastapi import APIRouter, HTTPException
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.models import users
from schemas.schema import User, UserCreate
from cryptography.fernet import Fernet
from typing import List


key = Fernet.generate_key()
f = Fernet(key)

user = APIRouter()

#OPERACAO GET PARA PBTER TODOS OS USUARIOS
@user.get("/users", response_model=List[User])
def get_users():
    try:
        result = conn.execute(users.select()).fetchall()
        # Converte os resultados para uma lista de dicionários
        users_list = [dict(row._mapping) for row in result]
        return users_list
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

#OPERACAO POST PARA CRIAR UM NOVO USUARIO
@user.post("/users", response_model=User)
def create_user(user: UserCreate):
    try:
        encrypted_password = f.encrypt(user.password.encode("utf-8")).decode("utf-8")
        new_user = {
            "name": user.name, 
            "email": user.email, 
            "password": encrypted_password,
            "role": user.role
        }
        
        result = conn.execute(users.insert().values(new_user))
        conn.commit()
        
        #Obter o id do usuario inserido
        inserted_id = result.lastrowid
        
        # Consultar o usuário recém-inserido
        query = select(users).where(users.c.id == inserted_id)
        inserted_user = conn.execute(query).first()
        
        #Converter o resultado a um dicionario aantes de devolver 
        inserted_user_dict = dict(inserted_user._asdict())
        
        #retorna inserted_user_dict
        return inserted_user_dict 
        
    except SQLAlchemyError as e: 
        print(str(e))
        return {"error": str(e)}

#OPERACAO GET PARA OBTER UM NUNICO USARIO POR ID
@user.get("/user/{id}")
def get_one_user(id: str):
    query = conn.execute(users.select().where(users.c.id == id)).first()
    query_dict = dict(query._asdict())
    return query_dict

#OPERACAO DELETE PARA EXCLUIR UM USARIO POR ID
@user.delete("/users/{id}")
def delete_user(id: int):
    try:
        query = users.delete().where(users.c.id == id)
        result = conn.execute(query)
        conn.commit()
        if result.rowcount > 0:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
#OPERACAO PUT PARA ATUALIZAR UM USUARIO POR ID
@user.put("/users/{id}", response_model=dict)
def update_user(id: int, user: UserCreate):
    try:
        encrypted_password = f.encrypt(user.password.encode("utf-8")).decode("utf-8")
        
        query = update(users).values(
            name=user.name,
            email=user.email,
            password=encrypted_password,
            role=user.role
        ).where(users.c.id == id)
        
        result = conn.execute(query)
        
        if result.rowcount > 0:
            return {"message": "User updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


