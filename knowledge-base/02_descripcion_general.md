# 02 — Descripción General del Sistema

## Stack Tecnológico

### Frontend

| Tecnología | Versión | Rol en el Sistema |
|------------|---------|-------------------|
| React + TypeScript | 18.x + 5.x | UI, enrutamiento, componentes |
| Vite | 5.x | Build tool y dev server (ES modules nativos, Rollup en producción) |
| Tailwind CSS | 3.x | Estilos utility-first con PostCSS y purging automático |
| TanStack Query | 5.x | Fetching, caché y sincronización de **datos del servidor** |
| TanStack Form | 0.x | Gestión de formularios con validación declarativa y tipado E2E |
| Zustand | 4.x | Estado global del **cliente**: carrito, sesión, pagos, UI |
| Axios | 1.x | Cliente HTTP con interceptores JWT y renovación automática |
| recharts | 2.x | Gráficos del dashboard de administración (barras, líneas, tortas) |
| @mercadopago/sdk-react | — | SDK oficial MercadoPago para tokenización PCI-compliant |

### Backend

| Tecnología | Versión | Rol en el Sistema |
|------------|---------|-------------------|
| FastAPI | 0.111+ | Framework REST + generación automática OpenAPI (Swagger/ReDoc) |
| SQLModel | 0.0.19+ | ORM + schemas Pydantic integrados (unifica modelo BD y validación) |
| PostgreSQL | 15+ | Base de datos relacional principal |
| Alembic | 1.13+ | Migraciones versionadas de base de datos |
| Passlib (bcrypt) | — | Hashing de contraseñas (cost factor ≥ 12) |
| mercadopago SDK | 2.3.0+ | SDK oficial MercadoPago Python para pagos y webhooks |
| slowapi | 0.1.9+ | Rate limiting por IP en endpoints críticos |
| python-jose / PyJWT | — | Generación y verificación de tokens JWT (algoritmo HS256) |

---

## Arquitectura del Backend — Capas

El backend implementa una **arquitectura en capas con flujo de dependencia unidireccional** y organización **feature-first** (vertical/modular).

```
Router → Service → UoW → Repository → Model
```

**Regla de oro:** Ninguna capa puede importar de la capa superior.

| Capa | Archivo | Responsabilidad | Conoce a |
|------|---------|-----------------|----------|
| **Router** | `router.py` | HTTP puro: parsear request, validar schema Pydantic, delegar al Service, serializar response. Sin lógica de negocio. | Service |
| **Service** | `service.py` | Lógica de negocio: stateless, orquesta operaciones sobre repositorios a través del UoW. Lanza HTTPException. No hace commit/rollback directamente. | UoW |
| **Unit of Work** | `core/uow.py` | Gestión de transacción: abre sesión de BD, provee acceso a repositorios, hace `commit()` al salir sin excepciones o `rollback()` si ocurre error. | Repository, Session |
| **Repository** | `repository.py` | Acceso a BD: queries sin lógica de negocio. Hereda de `BaseRepository[T]` genérico. Recibe la sesión del UoW por inyección. | Model, Session |
| **Model** | `model.py` | SQLModel tables + relaciones. Sin imports de capas superiores. Define la estructura de la BD. | Ninguna |

### Módulos Backend (Feature-First)

| Módulo | Ruta | Descripción |
|--------|------|-------------|
| `auth` | `app/modules/auth/` | Login, registro, refresh, logout. JWT access (30 min) + refresh (7 días). Rate limiting. |
| `refreshtokens` | `app/modules/refreshtokens/` | Modelo RefreshToken en BD para invalidación segura en logout. |
| `usuarios` | `app/modules/usuarios/` | CRUD usuarios + asignación de roles RBAC. Soft delete. |
| `direcciones` | `app/modules/direcciones/` | CRUD completo DireccionEntrega por usuario. PATCH /principal. |
| `categorias` | `app/modules/categorias/` | Categorías jerárquicas con CTE recursiva. Soft delete con validación. |
| `productos` | `app/modules/productos/` | Catálogo con Ingrediente (es_alergeno). Stock como campo en Producto. |
| `pedidos` | `app/modules/pedidos/` | Dominio central: máquina de estados FSM, audit trail, historial append-only. |
| `pagos` | `app/modules/pagos/` | Integración MercadoPago: crear pago, webhook IPN, registro de transacciones. |
| `admin` | `app/modules/admin/` | Dashboard con métricas, gestión de stock y usuarios desde el panel. |

Cada módulo contiene: `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`.

---

## Arquitectura del Frontend — Feature-Sliced Design (FSD)

El frontend aplica **Feature-Sliced Design**. El flujo de imports es unidireccional de arriba hacia abajo:

```
Pages → Features → Hooks/Stores → API → Types
```

Cada feature es autocontenida: sus componentes, hooks y estilos no son accesibles desde otras features.

| Capa | Contenido |
|------|-----------|
| `app/` | Providers, routing global, estilos globales |
| `pages/` | Solo define la ruta. Delega completamente a features. Sin lógica propia. |
| `widgets/` | Compone múltiples features en bloques de interfaz más grandes |
| `features/` | Interacciones de usuario autocontenidas (`feature/auth`, `feature/store`, `feature/pedidos`, `feature/admin`) |
| `hooks/` | Custom hooks con TanStack Query (`useProductos`, `usePedidos`, etc.) |
| `shared/stores/` | Stores Zustand (`authStore`, `cartStore`, `paymentStore`, `uiStore`) |
| `shared/api/` | Axios instance con interceptores Bearer + refresh 401 |
| `types/` | TypeScript global: `Producto`, `Pedido`, `Usuario`, `Pago`, `CartItem`, etc. |
| `components/` | UI genéricos: `Button`, `Input`, `Badge`, `Modal`, `Skeleton` |

### Separación Zustand / TanStack Query

> ⚠️ **Regla arquitectónica crítica:** Mezclar ambos tipos de estado en el mismo store es un error arquitectónico que debe evitarse.

| Librería | Gestiona | Ejemplos |
|----------|----------|---------|
| **Zustand** | Estado del **CLIENTE** | Carrito, sesión, proceso de pago, UI local (modales, sidebar) |
| **TanStack Query** | Estado del **SERVIDOR** | Productos, pedidos, dashboard. Datos remotos con caché automático. |

---

## API REST — Convenciones Globales

- Prefijo de rutas: `/api/v1`
- Errores: estándar **RFC 7807** (Problem Details): `{ "detail": "...", "code": "ERROR_CODE", "field": "..." }`
- Paginación: `GET /recursos?page=1&size=20` → `{ "items": [...], "total": N, "page": 1, "size": 20, "pages": P }`
- Soft delete: todos los GET filtran `WHERE deleted_at IS NULL` automáticamente
- Documentación interactiva: `/docs` (Swagger UI) y `/redoc` (ReDoc)

---

## Referencias Cruzadas

- → [03_actores_y_roles.md](03_actores_y_roles.md) — Actores y RBAC detallado
- → [04_modelo_de_datos.md](04_modelo_de_datos.md) — ERD completo
- → [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) — Diagramas y patrones
