from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import get_db

app = FastAPI(title="AI HRMS")


@app.get("/")
def root():
    return {
        "app": "AI HRMS",
        "docs": "/docs",
        "health_db": "/health/db",
    }


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    count = db.execute(text("SELECT COUNT(*) FROM employees")).scalar()
    return {"ok": True, "employees": count}