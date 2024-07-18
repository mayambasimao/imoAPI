from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.models import users
from config.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = conn.execute(users.select().where(users.c.email == payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return dict(user._mapping)  # Convertendo para um dicionário para facilitar o acesso aos dados

def is_seller(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "vendedor":
        raise HTTPException(status_code=403, detail="You do not have access to this resource")
    return current_user

def is_agent(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "agenteImob":
        raise HTTPException(status_code=403, detail="You do not have access to this resource")
    return current_user

def is_client(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "cliente":
        raise HTTPException(status_code=403, detail="You do not have access to this resource")
    return current_user

def is_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="You do not have access to this resource")
    return current_user
