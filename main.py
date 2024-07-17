from fastapi import FastAPI
from routes.user import user
from routes.crud_auth import auth_router

app = FastAPI()

app.include_router(user)
app.include_router(auth_router, prefix="/api/auth")
