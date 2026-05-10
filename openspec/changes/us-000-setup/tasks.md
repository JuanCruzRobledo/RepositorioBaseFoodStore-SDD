## 1. Backend — Estructura y dependencias

- [ ] 1.1 Crear estructura de carpetas `backend/app/{domain,application,infrastructure,presentation}/` con `__init__.py` cada una (ref: KB 08, sec. "Estructura de directorios")
- [ ] 1.2 Crear `backend/requirements.txt` con FastAPI, SQLModel, alembic, bcrypt, python-jose[cryptography], slowapi, python-dotenv (ref: KB 02, sec. "Stack tecnológico")
- [ ] 1.3 Crear `backend/.env.example` con todas las variables documentadas en design.md DD-06 (ref: KB 08, sec. "Variables de entorno")
- [ ] 1.4 Crear `backend/app/main.py` con FastAPI app, CORS middleware leyendo `CORS_ORIGINS`, endpoint `/health` que devuelve `{"status": "ok"}` (ref: design.md "Goals")

## 2. Backend — Configuración y base de datos

- [ ] 2.1 Crear `backend/app/infrastructure/db/session.py` con engine SQLModel y session factory leyendo `DATABASE_URL` (ref: KB 08)
- [ ] 2.2 Inicializar Alembic en `backend/alembic/` con `alembic init` y configurar `env.py` para leer `DATABASE_URL` desde `.env` (ref: KB 02)
- [ ] 2.3 Crear primera migración vacía `0001_initial.py` (placeholder, se llena en us-001-auth) (ref: design.md "Migration Plan")
- [ ] 2.4 Crear `backend/app/db/seed.py` con script `python -m app.db.seed` que inserta los 4 roles del sistema (ADMIN, STOCK, PEDIDOS, CLIENT) (ref: KB 04, sec. "Seed data")

## 3. Backend — BaseRepository y UnitOfWork

- [ ] 3.1 Test (TDD): `tests/infrastructure/test_base_repository.py` cubre los 3 scenarios del spec `repository-pattern` (get_by_id None, add no commitea, hereda métodos)
- [ ] 3.2 Implementar `backend/app/infrastructure/repositories/base.py` con `BaseRepository[T]` (ref: design.md DD-02 + spec `repository-pattern`)
- [ ] 3.3 Test (TDD): `tests/infrastructure/test_uow.py` cubre los 3 scenarios del spec `repository-pattern` (commit OK, rollback en excepción, expone repos)
- [ ] 3.4 Implementar `backend/app/infrastructure/uow.py` con `UnitOfWork` async context manager (ref: design.md DD-03 + spec `repository-pattern`)

## 4. Backend — Manejo de errores y dependencies

- [ ] 4.1 Crear `backend/app/presentation/exceptions/handlers.py` con exception handler global RFC 7807 (ref: spec `error-handling` + design.md DD-04)
- [ ] 4.2 Registrar el handler en `main.py` para `HTTPException`, `RequestValidationError` y `Exception` genérica
- [ ] 4.3 Crear `backend/app/presentation/dependencies/auth.py` con placeholders `get_current_user` y `require_role(...)` que levantan `NotImplementedError("Implementado en us-001-auth")` (ref: design.md "Risks")

## 5. Backend — Validación de inputs

- [ ] 5.1 Crear `backend/app/presentation/schemas/base.py` con `BaseSchema(BaseModel)` que aplica `model_config = ConfigDict(extra="forbid")` por default (ref: spec `input-validation`)
- [ ] 5.2 Documentar en `AGENTS.md` la regla: todos los schemas heredan de `BaseSchema` (no aceptan campos extra)

## 6. Frontend — Estructura y dependencias

- [ ] 6.1 Crear estructura `frontend/src/{app,features,entities,shared}/` con un `index.ts` cada una (ref: KB 08, sec. "Estructura frontend" + spec `monorepo-structure`)
- [ ] 6.2 Crear `frontend/package.json` con React, TypeScript, Vite, TanStack Query, TanStack Form, Zustand (con persist), Axios, Tailwind, Recharts (ref: KB 02)
- [ ] 6.3 Crear `frontend/.env.example` con `VITE_API_URL` y `VITE_MP_PUBLIC_KEY` (ref: KB 08)
- [ ] 6.4 Configurar `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `postcss.config.js` con valores estándar
- [ ] 6.5 Crear `frontend/index.html` y `frontend/src/main.tsx` que renderiza `<App />` con Router básico

## 7. Frontend — Stores Zustand

- [ ] 7.1 Crear `frontend/src/shared/stores/authStore.ts` (placeholder con `user` y `tokens`, persistido bajo `foodstore.auth`) (ref: design.md DD-05)
- [ ] 7.2 Crear `frontend/src/shared/stores/cartStore.ts` (placeholder con array de items, persistido bajo `foodstore.cart`)
- [ ] 7.3 Crear `frontend/src/shared/stores/uiStore.ts` (theme, modal abierto, persistido bajo `foodstore.ui`)
- [ ] 7.4 Crear `frontend/src/shared/stores/userStore.ts` (perfil del cliente, persistido bajo `foodstore.user`)

## 8. Frontend — Cliente HTTP y manejo global de errores

- [ ] 8.1 Crear `frontend/src/shared/api/client.ts` con instancia Axios apuntando a `VITE_API_URL` (ref: KB 02)
- [ ] 8.2 Crear interceptor de respuesta que aplica los 3 scenarios del spec `error-handling` (401 → redirect login, 5xx → toast genérico, 4xx → detail del problem+json)
- [ ] 8.3 Crear `frontend/src/app/ErrorBoundary.tsx` y montarlo en `main.tsx` (ref: design.md OQ-02)

## 9. Smoke tests y verificación

- [ ] 9.1 Backend: `pytest backend/tests/test_health.py` verifica que GET /health responde 200 con `{"status": "ok"}`
- [ ] 9.2 Backend: `alembic upgrade head` corre sin error en una DB vacía
- [ ] 9.3 Backend: `python -m app.db.seed` inserta los 4 roles sin error
- [ ] 9.4 Frontend: `npm run build` compila sin errores
- [ ] 9.5 Frontend: `npm run dev` levanta `:5173` y la página inicial renderiza

## 10. Documentación

- [ ] 10.1 Actualizar `README.md` raíz con los pasos de instalación post-clone (verificar que coincidan con design.md "Migration Plan")
- [ ] 10.2 Crear `backend/README.md` con setup específico del backend
- [ ] 10.3 Crear `frontend/README.md` con setup específico del frontend
