import os
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL", "")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True) if DATABASE_URL else None


def get_session() -> Session:
    if engine is None:
        raise RuntimeError("DATABASE_URL no esta configurado")
    return Session(engine)
