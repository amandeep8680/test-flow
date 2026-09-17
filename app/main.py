from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import AsyncSessionLocal


app = FastAPI(
    title="Test Flow API",
    version="1.0.0",
)


