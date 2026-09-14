import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .admin import setup_admin
from .api.auth import router as auth_router
from .api.health import router as health_router

app = FastAPI()

origins = [
    "http://localhost:5173",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SQLADMIN_SECRET_KEY"],
)
    
setup_admin(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}