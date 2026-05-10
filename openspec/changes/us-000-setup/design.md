## Context

Food Store arranca sin una sola línea de código. La KB define el stack (FastAPI + SQLModel + Postgres + React + Vite + Zustand) y los patrones esperados (Repository, Unit of Work, Feature-Sliced Design en frontend). Este change es la **única vez** en el roadmap que vamos a tocar estructura transversal — todos los changes posteriores agregan features sobre esta base.

**Constraints**:
- Stack fijo (definido en `02_descripcion_general.md`).
- Patrones obligatorios (definidos en `08_arquitectura_propuesta.md`): UoW, Repository, FSD, container-presentational.
- Variables de entorno y seguridad en `08_arquitectura_propuesta.md`.

**Stakeholders**: equipo de desarrollo (todo el aula). Decisiones tomadas acá impactan los próximos 9 changes.

## Goals / Non-Goals

**Goals:**
- Backend FastAPI levanta y responde `/health` con `200 OK`.
- Frontend Vite levanta en `:5173` y renderiza una shell vacía con routing básico.
- `BaseRepository[T]` y `UnitOfWork` están disponibles para que `us-001-auth` los use sin re-implementar.
- Stores Zustand persistidos están listos para que `us-001-auth` y `us-006-carrito` los usen.
- Errores backend siguen RFC 7807. Errores frontend tienen toast handler global.
- Migración Alembic inicial vacía aplicable (`alembic upgrade head` no falla).
- Seed data inicial mínimo (roles del sistema) corre con `python -m app.db.seed`.

**Non-Goals:**
- Endpoints de negocio (van en sus changes).
- Implementación real de auth (placeholders solamente).
- UI con páginas funcionales (solo shell).
- Docker / CI / observabilidad.
- Integración con MercadoPago (alcance de `us-008`).

## Decisions

### DD-01 — Backend organizado por capas hexagonales con feature-first dentro de cada capa
**Decisión**: la estructura es `backend/app/{domain,application,infrastructure,presentation}/` y dentro de cada capa los módulos se organizan por feature (`auth/`, `productos/`, etc., en changes futuros).
**Alternativas consideradas**:
- (a) Estructura plana por feature (`backend/app/{auth,productos,...}/`).
- (b) Capas estrictas sin sub-organización.
**Justificación**: la KB (`08_arquitectura_propuesta.md`) explicita "feature-first" + capas. Esta combinación da claridad de límites entre capas (testeo aislado del dominio) sin perder cohesión por feature.
**Trade-offs aceptados**: una feature toca 4 carpetas en lugar de 1 — más tabs abiertas pero mejor separación.

### DD-02 — `BaseRepository[T]` genérico con SQLModel + métodos `get_by_id`, `list`, `add`, `delete`
**Decisión**: una clase base genérica que recibe `Type[T]` y `Session` en el constructor, expone CRUD básico tipado. Los repositorios específicos heredan y agregan queries del dominio.
**Alternativas consideradas**:
- (a) Active Record (SQLModel ya lo permite).
- (b) Repositorios sin base, código duplicado.
**Justificación**: KB lo requiere (`08_arquitectura_propuesta.md`). Reduce boilerplate en los repositorios concretos sin acoplar el dominio a la infraestructura.
**Trade-offs**: la genericidad oculta queries que muchas veces se quiere tunear — pero los repos concretos pueden override.

### DD-03 — `UnitOfWork` como context manager async (`async with uow:`)
**Decisión**: clase `UnitOfWork` que abre la sesión, expone repositorios como atributos, y al cerrar hace commit/rollback automático.
**Alternativas consideradas**:
- (a) Pasar `Session` directamente a cada use case.
- (b) Decorador `@transactional`.
**Justificación**: claridad transaccional en use cases compuestos (ej. crear pedido = `add` ítems + decrementar stock + insertar audit). Single point para decidir commit/rollback.
**Trade-offs**: requiere que los use cases tengan acceso al UoW, no a repositorios sueltos — más boilerplate al inicio pero menos bugs transaccionales.

### DD-04 — Errores en formato RFC 7807 emitidos por exception handler global
**Decisión**: middleware FastAPI captura excepciones del dominio y devuelve `application/problem+json` con `type`, `title`, `status`, `detail`, `instance`.
**Alternativas consideradas**:
- (a) Errores ad-hoc en cada endpoint.
- (b) Estructura propia inventada.
**Justificación**: KB lo pide explícitamente (US-068). RFC 7807 es estándar — clientes pueden parsear de forma uniforme.
**Trade-offs**: los detalles internos (stack traces, IDs internos) NO van al cliente — solo `detail` legible. Logs internos guardan el resto.

### DD-05 — Frontend con FSD y stores Zustand persistidos en `localStorage`
**Decisión**: 4 stores definidos desde el inicio (`authStore`, `cartStore`, `uiStore`, `userStore`) con `persist` middleware de Zustand. Almacenamiento en `localStorage` con clave prefijada `foodstore.<store>`.
**Alternativas consideradas**:
- (a) Redux + redux-persist.
- (b) Context API.
**Justificación**: KB lo pide (`08_arquitectura_propuesta.md`). Zustand es liviano, sin boilerplate, y `persist` evita perder estado al refrescar.
**Trade-offs**: el carrito persistido en `localStorage` puede quedar desincronizado con el catálogo si pasa mucho tiempo — `us-007-pedidos` valida stock + precios al checkout (US-069/070).

### DD-06 — Variables de entorno
**Backend** (`.env.example`):
```
DATABASE_URL=postgresql://user:password@localhost:5432/foodstore
SECRET_KEY=cambia-esto-por-uno-de-64-caracteres
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
MP_ACCESS_TOKEN=TEST-placeholder    # se usa en us-008
MP_PUBLIC_KEY=TEST-placeholder      # se usa en us-008
```
**Frontend** (`.env.example`):
```
VITE_API_URL=http://localhost:8000
VITE_MP_PUBLIC_KEY=TEST-placeholder  # se usa en us-008
```

## Risks / Trade-offs

- **[Riesgo]** Dependency hell entre versiones de FastAPI y SQLModel. → **Mitigación**: pinear versiones específicas en `requirements.txt`.
- **[Riesgo]** El placeholder de `get_current_user` puede confundir si alguien lo usa antes de `us-001-auth`. → **Mitigación**: `raise NotImplementedError("Implementado en us-001-auth")` y documentado en docstring.
- **[Trade-off]** No instalamos pre-commit hooks ni linters en este change → simplifica el setup; el aula puede agregarlos después si lo desea.
- **[Trade-off]** No hay Docker en este change → corre todo nativo; `us-008` o un infra change puede dockerizar después.

## Migration Plan

(No aplica — es el primer change del proyecto, no hay migración desde un estado previo.)

Pasos de instalación post-merge:
1. `cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
2. `cp .env.example .env` y completar `DATABASE_URL` real.
3. `alembic upgrade head`
4. `python -m app.db.seed`
5. `uvicorn app.main:app --reload` → verificar `http://localhost:8000/health`.
6. `cd frontend && npm install && cp .env.example .env`
7. `npm run dev` → verificar `http://localhost:5173`.

## Open Questions

- **OQ-01**: ¿el seed inicial incluye un usuario ADMIN preexistente? Decisión propuesta: **sí**, con email `admin@foodstore.local` y password de `.env` (`SEED_ADMIN_PASSWORD`). Bloquea `us-001-auth` si no se resuelve. (Ver IN-01 en `10_preguntas_abiertas.md`.)
- **OQ-02**: ¿el Frontend tiene un `ErrorBoundary` global desde el inicio o se posterga? Decisión propuesta: **sí**, mínimo, en `app/`. No bloquea changes posteriores.
