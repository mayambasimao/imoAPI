from fastapi import FastAPI
from routes.user import user
from routes.house_router import house_router
from routes.crud_auth import auth_router
from routes.client_router import client_router
from routes.agent_router import agent_router

app = FastAPI()

#app.include_router(user)
app.include_router(auth_router, prefix="/api/auth")
app.include_router(house_router)
app.include_router(client_router)
app.include_router(agent_router)

