from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.database import AsyncSessionLocal
from core.cors import setup_cors

app = FastAPI(
    title="Test Flow API",
    version="1.0.0",
)
setup_cors(app)

app.include_router(api_router)
