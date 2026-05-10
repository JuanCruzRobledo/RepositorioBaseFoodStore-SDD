# Backend — Food Store

FastAPI + SQLModel + PostgreSQL.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate              # Windows
# source .venv/bin/activate         # Linux/Mac

pip install -r requirements.txt
cp .env.example .env                # completar DATABASE_URL real

alembic upgrade head
python -m app.db.seed

uvicorn app.main:app --reload
```

API en `http://localhost:8000` · Docs en `http://localhost:8000/docs`

## Tests

```bash
pytest -v
```

## Estructura

```
backend/app/
├── domain/              capa de dominio (entidades + reglas)
├── application/         casos de uso, orquestacion (UoW)
├── infrastructure/      repositorios, sesiones, integraciones externas
│   ├── db/              session.py + engine SQLModel
│   ├── repositories/    BaseRepository[T] generico
│   └── uow.py           UnitOfWork async context manager
└── presentation/        routers, schemas Pydantic, dependencies
    ├── exceptions/      handlers RFC 7807
    ├── dependencies/    auth placeholders (us-001-auth los reemplaza)
    └── schemas/         BaseSchema con extra=forbid
```
