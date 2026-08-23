from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from models.ping import Ping

# This line creates any tables that don't exist yet, based on your models.
# (Fine for Day 2 throwaway testing — from Day 3 onward we switch to Alembic
# migrations instead of this, so schema changes are tracked properly.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinShield Core API")


@app.get("/health")
def health_check():
    """Confirms the API process itself is up."""
    return {"status": "ok"}


@app.post("/ping")
def create_ping(db: Session = Depends(get_db)):
    """Writes a row to Postgres — proves FastAPI can write to the DB."""
    row = Ping(message="pong")
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "message": row.message}


@app.get("/ping")
def list_pings(db: Session = Depends(get_db)):
    """Reads rows back from Postgres — proves FastAPI can read from the DB."""
    rows = db.query(Ping).all()
    return [{"id": r.id, "message": r.message} for r in rows]