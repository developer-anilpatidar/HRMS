from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import me as me_api
from app.db import get_db

app = FastAPI(title="AI HRMS")
app.include_router(me_api.router)


@app.get("/")
def root():
    return {
        "app": "AI HRMS",
        "docs": "/docs",
        "health_db": "/health/db",
        "me": "/me",
    }


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    count = db.execute(text("SELECT COUNT(*) FROM employees")).scalar()
    return {"ok": True, "employees": count}