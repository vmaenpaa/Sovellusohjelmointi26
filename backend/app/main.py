import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .admin import setup_admin
from .api.activity_types import router as activity_types_router
from .api.auth import router as auth_router
from .api.calendar import router as calendar_router
from .api.goals import router as goals_router
from .api.health import router as health_router
from .api.plans import router as plans_router
from .api.sessions import router as sessions_router
from .core.config import Settings

app = FastAPI()

settings = Settings()
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(activity_types_router)
app.include_router(sessions_router)
app.include_router(calendar_router)
app.include_router(plans_router)
app.include_router(goals_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SQLADMIN_SECRET_KEY"],
)
    
setup_admin(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}