## Why

Food Store no tiene infraestructura base implementada. Los siguientes 9 changes del roadmap (`us-001-auth` en adelante) asumen que existe estructura de directorios, dependencias instaladas, base de datos accesible, primitivas comunes (`BaseRepository`, `UnitOfWork`) y stores Zustand listos. Sin esto, ningún change posterior puede ejecutarse: no hay dónde poner el código, no hay forma de persistir, no hay manejo uniforme de errores, ni protección básica contra XSS/SQLi.

Este change establece esa base **una sola vez** para que los 9 changes siguientes puedan enfocarse en lógica de dominio sin re-resolver problemas transversales.

## What Changes

- **Monorepo backend** (`backend/`): estructura feature-first con capas `domain/`, `application/`, `infrastructure/`, `presentation/`. FastAPI + SQLModel + Alembic + bcrypt + python-jose + slowapi como dependencias core.
- **Monorepo frontend** (`frontend/`): estructura Feature-Sliced Design (`app/`, `features/`, `entities/`, `shared/`). React + TypeScript + Vite + TanStack Query + TanStack Form + Zustand + Axios + Tailwind como dependencias core.
- **Infraestructura backend**: `BaseRepository[T]` genérico, `UnitOfWork` para transacciones atómicas, dependencies FastAPI (`get_current_user`, `require_role`) como placeholders preparados para `us-001-auth`.
- **Infraestructura frontend**: 4 stores Zustand persistidos (`authStore`, `cartStore`, `uiStore`, `userStore`), cliente Axios con interceptor base.
- **Manejo de errores estandarizado**: middleware de excepciones FastAPI emitiendo formato RFC 7807 (`application/problem+json`).
- **Validación y sanitización de inputs**: validación Pydantic estricta, escape de salida en frontend para anti-XSS, uso obligatorio de SQLModel ORM (no SQL crudo) para anti-SQLi.
- **Configuración**: `.env.example` backend y frontend, conexión Postgres, primera migración Alembic vacía, seed data inicial mínimo (roles del sistema).

Dependencias de la KB que respaldan la propuesta:
- `knowledge-base/02_descripcion_general.md` — stack tecnológico.
- `knowledge-base/08_arquitectura_propuesta.md` — patrones (UoW, Repository), estructura de directorios, variables de entorno, seguridad.
- `knowledge-base/04_modelo_de_datos.md` — entidades y seed inicial.
- `knowledge-base/06_funcionalidades.md` — US-000, US-000a-e, US-068, US-074.

## Capabilities

### New Capabilities

- `monorepo-structure`: define la estructura de directorios obligatoria del backend (capas hexagonales) y frontend (FSD), nombres de carpetas reservadas y separación de responsabilidades por capa.
- `repository-pattern`: contrato del `BaseRepository[T]` genérico y `UnitOfWork` para transacciones atómicas multi-repositorio.
- `error-handling`: contrato del formato de error RFC 7807 emitido por la API y del manejo global de errores en el frontend (toast/redirect según código HTTP).
- `input-validation`: reglas de validación de inputs en backend (Pydantic estricto) y de escape en frontend (anti-XSS), prohibición de SQL crudo.

### Modified Capabilities

(Ninguna — es el primer change del proyecto.)

## Impact

- **Código nuevo**: ~30-40 archivos entre backend y frontend (estructura de directorios, archivos `__init__.py`, configs, base classes).
- **Dependencias**: `requirements.txt` backend y `package.json` frontend con todas las dependencias core del stack v5.0.
- **Variables de entorno nuevas**: `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `CORS_ORIGINS` (backend); `VITE_API_URL` (frontend). MercadoPago se documenta en este change pero se usa en `us-008`.
- **APIs**: ningún endpoint funcional — solo `/health` para verificar que el backend levanta.
- **Sistemas afectados**: ninguno previo (es el primer change).

## Non-goals

Este change explícitamente **NO** incluye:
- Ningún endpoint de negocio (auth, productos, pedidos, etc.) — eso va en sus respectivos changes.
- Implementación real de `get_current_user` ni `require_role` — solo placeholders que `us-001-auth` reemplazará.
- Frontend con páginas funcionales — solo el shell de la app y los stores vacíos.
- Tests funcionales del dominio — solo un test de smoke que verifica que `/health` responde.
- Integración con MercadoPago — eso es alcance de `us-008-pagos-mercadopago`.
- Docker / CI / observabilidad — fuera de alcance de este change; ver `infra-observability` (no priorizado).
