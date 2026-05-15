# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **Food Store**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
C-01 foundation-setup
  └── C-02 auth                                ← desbloquea TODO lo demás
        │
        ├── C-03 categorias-ingredientes
        │     └── C-04 productos
        │           └── C-07 carrito
        │                 │
        ├── C-05 perfil-cliente                ← paralelo con C-03, C-06
        │
        └── C-06 direcciones                   ← paralelo con C-03, C-05
              │
              └── (junto con C-07)
                    └── C-08 pedidos
                          └── C-09 pagos-mercadopago
                                └── C-10 admin
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → C-01 foundation-setup (solo)

GATE 1: C-01 ✓
  → C-02 auth (solo)

GATE 2: C-02 ✓                                 ← PRIMER FORK (3 paralelos)
  → C-03 categorias-ingredientes               [Agente A — Backend]
  → C-05 perfil-cliente                        [Agente B — Fullstack]
  → C-06 direcciones                           [Agente C — Fullstack]

GATE 3: C-03 ✓
  → C-04 productos                             [Agente A]

GATE 4: C-04 ✓
  → C-07 carrito                               [Agente C — frontend pesado]

GATE 5: C-07 + C-06 ✓                          ← punto de sincronización
  → C-08 pedidos                               [Agente A — backend pesado]

GATE 6: C-08 ✓
  → C-09 pagos-mercadopago                     [Agente A]

GATE 7: C-09 ✓
  → C-10 admin                                 [Agente A]
```

### Camino crítico (8 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-04 → C-07 → C-08 → C-09 → C-10
```

> Los changes C-05 (perfil) y C-06 (direcciones) son **paralelizables** y no bloquean ningún otro change directamente (excepto C-06 → C-08).
> Si tu prioridad es llegar a una versión vendible con pago, podés postergar C-05 y C-10 sin afectar el flujo principal.

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core)            │ Agente B (Fullstack)         │ Agente C (Frontend)
─────┼────────────────────────────────────┼──────────────────────────────┼─────────────────────────
  1  │ C-01 foundation-setup              │              —               │              —
  2  │ C-02 auth                          │              —               │              —
  3  │ C-03 categorias-ingredientes       │ C-05 perfil-cliente          │ C-06 direcciones
  4  │ C-04 productos                     │              —               │              —
  5  │              —                     │              —               │ C-07 carrito
  6  │ C-08 pedidos                       │              —               │              —
  7  │ C-09 pagos-mercadopago             │              —               │              —
  8  │ C-10 admin                         │              —               │              —
```

> El plan termina en 8 pasos con paralelización moderada. Sin paralelización, serían 10 pasos secuenciales.

---

## FASE 0 — Cimientos

### [C-01] `foundation-setup`
- **Estado**: `[ ]` pendiente
- **Scope**: Scaffolding completo del monorepo + infraestructura base + primitivas transversales
  - Estructura backend: `backend/app/{domain,application,infrastructure,presentation}/` con `__init__.py` en cada capa
  - Estructura frontend: `frontend/src/{app,features,entities,shared}/` siguiendo Feature-Sliced Design
  - Backend: FastAPI app mínima con `GET /health`, CORS configurado, `requirements.txt` con todas las dependencias core (FastAPI, SQLModel, Alembic, bcrypt, python-jose, slowapi)
  - `BaseRepository[T]` genérico en `backend/app/infrastructure/repositories/base.py` con `get_by_id`, `list`, `add`, `delete`
  - `UnitOfWork` async context manager en `backend/app/infrastructure/uow.py` con commit/rollback automático
  - Exception handlers RFC 7807 en `backend/app/presentation/exceptions/handlers.py` para `HTTPException`, `RequestValidationError`, `Exception`
  - Placeholders `get_current_user` y `require_role` en `backend/app/presentation/dependencies/auth.py` que levantan `NotImplementedError` (reemplazados en C-02)
  - `BaseSchema(BaseModel)` con `model_config = ConfigDict(extra='forbid')` en `backend/app/presentation/schemas/base.py`
  - Alembic inicializado en `backend/alembic/` con migración 001 vacía + tabla `roles`
  - Seed inicial `python -m app.db.seed` que inserta los 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT)
  - Frontend: Vite + React 18 + TypeScript + Tailwind + path aliases (`@app`, `@features`, `@entities`, `@shared`)
  - 4 stores Zustand persistidos: `authStore`, `cartStore`, `uiStore`, `userStore` con prefijo `foodstore.<store>`
  - Cliente Axios con interceptor global aplicando los 3 scenarios del spec error-handling (401 → redirect login, 5xx → toast, 4xx → detail)
  - `ErrorBoundary` global en `frontend/src/app/`
  - `.env.example` backend y frontend con todas las variables documentadas
  - Tests: smoke `GET /health` + 3 scenarios `BaseRepository` + 3 scenarios `UnitOfWork`
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` (propósito del sistema, alcance v5.0)
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios + §Patrones (UoW, Repository)
  - `knowledge-base/06_funcionalidades.md` §EPIC 00 (US-000, US-068, US-074)

---

## FASE 1A — Autenticación

### [C-02] `auth`
- **Estado**: `[ ]` pendiente
- **Scope**: Sistema completo de autenticación JWT + RBAC con 4 roles + guards FE/BE
  - Modelos: `User`, `RefreshToken`, relación con `Role` (creado en seed de C-01)
  - `POST /api/auth/register` — registro de cliente con rol CLIENT automático
  - `POST /api/auth/login` — JWT access (30 min) + refresh (7 días), respuesta ambigua en credenciales inválidas, rate limiting 5/IP/15min
  - `POST /api/auth/refresh` — rotación de refresh token, detección de replay attack (revoca toda la cadena)
  - `POST /api/auth/logout` — revocación del refresh token en BD
  - `GET /api/auth/me` — info del usuario autenticado
  - `PATCH /api/admin/users/{id}/roles` — asignación de roles por ADMIN, protección del último ADMIN
  - `require_role()` y `require_admin()` dependencies reemplazando los placeholders de C-01
  - Migración 002: tablas `users`, `refresh_tokens`, `user_roles` (M2M)
  - Frontend: páginas `/login`, `/register`, navegación adaptada por rol, guards de rutas
  - Interceptor Axios: renovación transparente del access token al expirar, sin reentrancia
  - `useAuthStore` con setters de sesión, logout, persistencia
  - Tests: login correcto, token expirado, rate limit, refresh con rotación, replay attack detectado, RBAC en endpoints protegidos
- **Dependencias**: C-01
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` (4 roles del sistema, matriz RBAC)
  - `knowledge-base/05_reglas_de_negocio.md` §Autenticación (RN-AU)
  - `knowledge-base/07_flujos_principales.md` §Flujo auth (login + refresh)
  - `knowledge-base/06_funcionalidades.md` §EPIC 01 (US-001 a US-006, US-066, US-067, US-073, US-075, US-076)

---

## FASE 1B — Catálogo y dominio base

> Los changes C-03, C-05 y C-06 pueden proponerse en paralelo. C-03 debe archivarse antes de C-04.

### [C-03] `categorias-ingredientes`
- **Estado**: `[ ]` pendiente
- **Scope**: CRUD jerárquico de categorías + CRUD de ingredientes con flag alérgeno
  - Modelos: `Category` (jerárquica con `parent_id`), `Ingredient` (con `es_alergeno: bool`)
  - `CategoryService` con CTE recursivo para listado anidado, validación anti-ciclos en `parent_id`
  - Endpoints categorías: CRUD `/api/admin/categories` (rol ADMIN/STOCK), listado público `GET /api/public/categories` anidado
  - Endpoints ingredientes: CRUD `/api/admin/ingredients` paginado, filtrable por `es_alergeno`
  - Soft delete en ambas entidades, validación de que no haya productos activos antes de borrar categoría
  - Migración 003: tablas `categories`, `ingredients`
  - Tests: CRUD, jerarquía (anti-ciclos), soft delete con productos asociados, RBAC
- **Dependencias**: C-02
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Category + §Ingredient
  - `knowledge-base/06_funcionalidades.md` §EPIC 03 (US-007 a US-010) + §EPIC 04 (US-011 a US-014)
  - `knowledge-base/05_reglas_de_negocio.md` §Categorías + §Ingredientes

---

### [C-04] `productos`
- **Estado**: `[ ]` pendiente
- **Scope**: Productos con stock atómico + M2M con categorías e ingredientes + catálogo público filtrable
  - Modelos: `Product`, `ProductCategory` (M2M), `ProductIngredient` (M2M con `es_removible: bool`)
  - Precio en `DECIMAL(10,2)` con validación `> 0` y máximo 2 decimales
  - Stock atómico con SELECT FOR UPDATE en actualizaciones (nunca negativo)
  - Endpoints admin: CRUD `/api/admin/products`, asociación M2M `POST /api/admin/products/{id}/categories`, `POST /api/admin/products/{id}/ingredients`
  - Endpoints públicos: listado `GET /api/public/products` con filtros (categoría, nombre, disponibilidad, exclusión por alérgeno), paginación
  - `GET /api/public/products/{id}` — detalle con ingredientes, alérgenos, categorías
  - Soft delete preservando datos en pedidos históricos
  - Migración 004: tablas `products`, `product_categories`, `product_ingredients`
  - Tests: CRUD, stock atómico bajo concurrencia, filtros del catálogo público, exclusión por alérgeno
- **Dependencias**: C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Product + §ProductCategory + §ProductIngredient
  - `knowledge-base/05_reglas_de_negocio.md` §Productos + §Stock
  - `knowledge-base/06_funcionalidades.md` §EPIC 05 (US-015 a US-023)
  - `knowledge-base/07_flujos_principales.md` §Flujo catálogo

---

## FASE 1C — Perfil y direcciones del cliente

> Los changes C-05 y C-06 son **independientes** entre sí y pueden proponerse en paralelo con C-03. Ambos dependen solo de C-02.

### [C-05] `perfil-cliente`
- **Estado**: `[ ]` pendiente
- **Scope**: Ver y editar perfil propio + cambio de contraseña con invalidación masiva de refresh tokens
  - `GET /api/profile/me` — datos propios (nombre, email, teléfono, fecha de registro)
  - `PATCH /api/profile/me` — editar nombre y teléfono. Email NO editable.
  - `POST /api/profile/change-password` — verificar contraseña actual + nueva mínima 8 chars + invalidación masiva de todos los refresh tokens del usuario
  - Frontend: página `/perfil` con form TanStack Form, validación client-side y server-side
  - Tests: ver perfil propio (no de otros), editar campos permitidos, rechazar cambio de email, cambio de password con invalidación
- **Dependencias**: C-02
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §EPIC 06 (US-061 a US-063)
  - `knowledge-base/05_reglas_de_negocio.md` §Perfil
  - `knowledge-base/03_actores_y_roles.md` §CLIENT permissions

---

### [C-06] `direcciones`
- **Estado**: `[ ]` pendiente
- **Scope**: CRUD direcciones del cliente con regla de predeterminada única
  - Modelo: `Address` (calle, número, piso/depto, ciudad, CP, `es_predeterminada: bool`, FK a User)
  - Endpoints: `GET /api/addresses`, `POST`, `PATCH /{id}`, `DELETE /{id}` (todos validan ownership por JWT)
  - Primera dirección creada se marca `es_predeterminada = true` automáticamente
  - Transacción para cambio de predeterminada: quita flag anterior + setea en nueva (atómico)
  - Al eliminar la predeterminada, reasignar automáticamente a la siguiente más reciente
  - Migración 005: tabla `addresses`
  - Frontend: página `/direcciones` con lista + modal de creación/edición, marcador visual de predeterminada
  - Tests: ownership (un usuario no ve direcciones de otro), primera = predeterminada, transacción de cambio, reasignación al borrar
- **Dependencias**: C-02
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Address
  - `knowledge-base/06_funcionalidades.md` §EPIC 07 (US-024 a US-028)
  - `knowledge-base/05_reglas_de_negocio.md` §Direcciones

---

## FASE 2 — Carrito (frontend pesado)

### [C-07] `carrito`
- **Estado**: `[ ]` pendiente
- **Scope**: Carrito 100% client-side con Zustand persistido + personalización por exclusión de ingredientes
  - `cartStore` ya creado en C-01 — acá se completa la lógica
  - Acciones: `addItem`, `setQuantity`, `removeItem`, `clear`, `total`, `excludeIngredient`, `restoreIngredient`
  - Acumulación: si el producto ya está en el carrito (con la misma combinación de exclusiones), suma cantidad
  - Personalización: solo permite excluir ingredientes que el producto tenga marcados como `es_removible = true`
  - Cantidad 0 elimina el ítem
  - Vaciar requiere confirmación modal
  - Frontend: páginas `/carrito` con resumen reactivo (subtotal por ítem, total general), botón checkout deshabilitado si vacío
  - Componente `ProductCard` con botón "Agregar al carrito" + modal de personalización
  - Tests: agregar producto, acumular si existe, personalizar exclusiones, modificar cantidad, persistencia tras refresh
- **Dependencias**: C-04
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §EPIC 08 (US-029 a US-034)
  - `knowledge-base/05_reglas_de_negocio.md` §Carrito + §Personalización
  - `knowledge-base/07_flujos_principales.md` §Flujo de creación de pedido (parte de carrito)

---

## FASE 3 — Pedidos

### [C-08] `pedidos`
- **Estado**: `[ ]` pendiente
- **Scope**: Creación atómica de pedidos con UoW + snapshots + FSM 6 estados + audit trail append-only
  - Modelos: `Pedido`, `DetallePedido`, `HistorialEstadoPedido` (append-only, FK a actor)
  - FSM: PENDIENTE → CONFIRMADO → EN_PREPARACIÓN → EN_CAMINO → ENTREGADO, + CANCELADO terminal desde cualquier estado
  - Validaciones pre-checkout: stock disponible para cada ítem + precios actualizados (notifica si cambió desde que se agregó al carrito)
  - Creación atómica con UoW (creado en C-01): `BEGIN → SELECT FOR UPDATE stock → crear Pedido → crear DetallePedido con snapshots de precio → decrementar stock → COMMIT`
  - `precio_snapshot` en cada `DetallePedido` (no se recalcula al cambiar el precio del catálogo)
  - `direccion_snapshot` en `Pedido` (JSON congelado de la dirección al momento del pedido)
  - Estado inicial PENDIENTE, vacía el carrito al crear
  - Transiciones de FSM: PENDIENTE → CONFIRMADO automático por C-09 (pago aprobado), el resto manual por rol PEDIDOS
  - Restauración de stock al CANCELAR desde CONFIRMADO o estados posteriores
  - Endpoints: `POST /api/pedidos` (validate + create), `GET /api/pedidos/me` (propios, paginado, filtro por estado), `GET /api/admin/pedidos` (todos, ADMIN/PEDIDOS), `GET /api/pedidos/{id}` (detalle con ownership o admin), `PATCH /api/admin/pedidos/{id}/estado` (transición manual con razón)
  - Migración 006: tablas `pedidos`, `detalle_pedidos`, `historial_estado_pedidos`
  - Tests: validación pre-checkout (stock, precios), creación atómica (rollback ante error), snapshots correctos, FSM (transiciones válidas, inválidas), restauración de stock, audit trail completo, RBAC en listados
- **Dependencias**: C-07, C-06
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Pedido + §DetallePedido + §HistorialEstadoPedido
  - `knowledge-base/05_reglas_de_negocio.md` §Pedidos + §FSM + §Snapshots
  - `knowledge-base/07_flujos_principales.md` §Flujo de creación de pedido (UoW completo)
  - `knowledge-base/06_funcionalidades.md` §EPIC 09 + §EPIC 10 + §EPIC 12 + §EPIC 13
  - `knowledge-base/08_arquitectura_propuesta.md` §UoW + §Audit trail
  - `knowledge-base/10_preguntas_abiertas.md` §IN-05 (verificación de precios)

---

## FASE 4 — Integración de pagos

### [C-09] `pagos-mercadopago`
- **Estado**: `[ ]` pendiente
- **Scope**: Integración con MercadoPago Checkout API + webhook IPN + transición automática de FSM
  - Variables de entorno requeridas: `MP_ACCESS_TOKEN`, `MP_PUBLIC_KEY`
  - `MercadoPagoGateway` siguiendo abstracción `PaymentGateway` (preparado para futuros PSPs)
  - `POST /api/pagos/preferencia` — crea preferencia MP con `idempotency_key` único por pedido, devuelve `preference_id` y URL de checkout
  - `POST /api/pagos/webhook` — recibe IPN de MP, verifica firma, actualiza estado del pago
  - Tokenización PCI SAQ-A en el browser (no se almacena tarjeta en backend)
  - Transición automática PENDIENTE → CONFIRMADO al aprobarse el pago (dispara la FSM definida en C-08)
  - Reintento de pago rechazado: nuevo `idempotency_key`, el pedido sigue en PENDIENTE hasta que se apruebe
  - `GET /api/pagos/{pedido_id}` — estado, monto, fecha (solo pedidos propios o admin)
  - Modelo: `Pago` con FK a `Pedido`, estado (PENDIENTE/APROBADO/RECHAZADO), `mp_payment_id`, `mp_status`, `idempotency_key`, fecha
  - Frontend: página `/pago/{pedido_id}` que usa MercadoPago SDK frontend, integra checkout, captura retorno (success/failure/pending)
  - Pantalla de confirmación con resumen del pedido y link al pago
  - Migración 007: tabla `pagos`
  - Tests: creación de preferencia idempotente, webhook con firma válida e inválida, transición de FSM al aprobarse, reintento con nuevo idempotency_key, consulta de estado con ownership
- **Dependencias**: C-08
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Pago
  - `knowledge-base/05_reglas_de_negocio.md` §Pagos + §Idempotencia
  - `knowledge-base/07_flujos_principales.md` §Flujo de pago (webhook IPN)
  - `knowledge-base/06_funcionalidades.md` §EPIC 11 + §EPIC 14
  - `knowledge-base/08_arquitectura_propuesta.md` §PaymentGateway

---

## FASE 5 — Panel administrativo

### [C-10] `admin`
- **Estado**: `[ ]` pendiente
- **Scope**: Panel administrativo completo con gestión de usuarios + control total de catálogo y pedidos + dashboard de métricas
  - Endpoints:
    - `GET /api/admin/usuarios` — listado paginado, búsqueda por nombre/email, filtro por rol
    - `PATCH /api/admin/usuarios/{id}` — editar roles, activar/desactivar (invalida refresh tokens del usuario modificado)
    - `DELETE /api/admin/usuarios/{id}` — baja lógica + invalidación masiva de refresh tokens
    - `GET /api/admin/metricas/resumen` — pedidos por estado, ingresos del mes, productos más vendidos del mes
    - Endpoints admin de catálogo y pedidos ya existen desde C-03/C-04/C-08, acá se agregan vistas frontend que los consumen
  - Frontend: layout admin con sidebar dedicada, páginas:
    - `/admin/dashboard` — KPIs principales con Recharts (pedidos por estado, ingresos mensuales, top productos)
    - `/admin/usuarios` — tabla con filtros, edición inline de roles
    - `/admin/pedidos` — tabla con filtros por estado, fecha, búsqueda, transición de estado con razón obligatoria
    - `/admin/catalogo` — accesos rápidos a CRUD de categorías, ingredientes, productos (vistas ya armadas en C-03/C-04)
  - RBAC: solo ADMIN accede a `/admin/usuarios` y `/admin/dashboard`. ADMIN y STOCK ven `/admin/catalogo`. ADMIN y PEDIDOS ven `/admin/pedidos`.
  - Tests: listado de usuarios paginado, edición con invalidación de tokens, métricas correctas con datos seed, RBAC en cada ruta admin
- **Dependencias**: C-09
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §ADMIN + §STOCK + §PEDIDOS
  - `knowledge-base/06_funcionalidades.md` §EPIC 15 + §EPIC 16
  - `knowledge-base/05_reglas_de_negocio.md` §Administración
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrón admin layout

---

## Resumen

- **Total de changes**: 10
- **Camino crítico**: 8 changes
- **Gates de paralelismo**: 5 (uno con FORK de 3 paralelos en GATE 2)
- **Changes paralelizables**: C-05 (perfil) y C-06 (direcciones) con C-03 (cat/ingr)
- **Tiempo estimado solo**: 25 a 35 horas con un único desarrollador
- **Tiempo estimado con 3 agentes**: 18 a 24 horas

**Primer change recomendado**: `C-01 foundation-setup`. Para arrancar: `/opsx:propose C-01-foundation-setup`.
