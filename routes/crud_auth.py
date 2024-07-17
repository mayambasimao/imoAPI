from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from config.db import conn
from models.models import users
from schemas.schema import User, UserCreate, TokenData
from config.auth import create_access_token, verify_password, get_password_hash, decode_access_token

auth_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@auth_router.post("/register", response_model=User)
def register_user(user: UserCreate):
    try:
        hashed_password = get_password_hash(user.password)
        new_user = {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
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
        raise HTTPException(status_code=500, detail="Internal Server Error")

@auth_router.post("/login", response_model=TokenData)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = conn.execute(users.select().where(users.c.email == form_data.username)).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        user_dict = dict(user._mapping)
        if not verify_password(form_data.password, user_dict["password"]):
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        access_token = create_access_token(data={"sub": user_dict["email"], "name": user_dict["name"], "role": user_dict["role"]})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "name": user_dict["name"],
            "role": user_dict["role"]
        }
    
    except SQLAlchemyError as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = conn.execute(users.select().where(users.c.email ==  payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return dict(user._mapping)