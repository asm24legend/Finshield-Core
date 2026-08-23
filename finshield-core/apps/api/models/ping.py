from sqlalchemy import Column, Integer, String
from db import Base


class Ping(Base):
    """
    Throwaway table used only to confirm FastAPI <-> Postgres works.
    Delete this once real models (entities, cases, etc.) exist.
    """
    __tablename__ = "ping"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, default="pong")