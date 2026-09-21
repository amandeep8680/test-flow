from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.database import AsyncSessionLocal
from app.core.cors import setup_cors
from app.exception.exception_handlers import register_exception_handlers
app = FastAPI(
    title="Test Flow API",
    version="1.0.0",
)
setup_cors(app)
register_exception_handlers(app)

app.include_router(api_router)
