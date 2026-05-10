"""
Seed inicial: inserta los 4 roles del sistema (ADMIN, STOCK, PEDIDOS, CLIENT).
Uso:  python -m app.db.seed
"""
from __future__ import annotations

from app.infrastructure.db.session import engine
from sqlmodel import Session, text


ROLES = ["ADMIN", "STOCK", "PEDIDOS", "CLIENT"]


def seed() -> None:
    if engine is None:
        raise RuntimeError("DATABASE_URL no esta configurado")
    with Session(engine) as session:
        for role in ROLES:
            session.execute(
                text("INSERT INTO roles (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                {"name": role},
            )
        session.commit()
    print(f"Seed OK — roles insertados: {', '.join(ROLES)}")


if __name__ == "__main__":
    seed()
