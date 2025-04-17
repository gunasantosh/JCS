from fastapi import FastAPI
from app.api.routes import users, core

app = FastAPI(title="My FastAPI App")

# Include routers
app.include_router(users.router)
app.include_router(core.router)

