import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agents.checkpoint import close_checkpointer, init_checkpointer
from app.api import chat as chat_api
from app.api import leave as leave_api
from app.api import me as me_api
from app.db import get_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_checkpointer()
    yield
    close_checkpointer()


app = FastAPI(title="AI HRMS", lifespan=lifespan)

_cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(me_api.router)
app.include_router(leave_api.router)
app.include_router(chat_api.router)


@app.get("/")
def root():
    return {
        "app": "AI HRMS",
        "docs": "/docs",
        "health_db": "/health/db",
        "me": "/me",
        "leave": "/leave/types",
        "chat": "/chat",
    }


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    count = db.execute(text("SELECT COUNT(*) FROM employees")).scalar()
    return {"ok": True, "employees": count}
