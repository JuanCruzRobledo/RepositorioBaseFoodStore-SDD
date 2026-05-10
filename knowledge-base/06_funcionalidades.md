# 06 — Funcionalidades del Sistema

Organizado por épicas de implementación siguiendo el orden lógico de dependencias.

---

## EPIC 00 — Infraestructura y Setup (Sprint 0)

| Historia | Funcionalidad |
|----------|--------------|
| US-000 | Scaffolding del monorepo: estructura backend (feature-first) y frontend (FSD) |
| US-000a | Setup del backend con FastAPI + SQLModel + Alembic + dependencias core |
| US-000b | Configuración PostgreSQL, migraciones Alembic y seed data |
| US-000c | Setup del frontend con React + TypeScript + Vite + dependencias |
| US-000d | Implementación de BaseRepository[T], Unit of Work y dependencias FastAPI (`get_current_user`, `require_role`) |
| US-000e | Configuración de los 4 stores Zustand con persistencia |
| US-068 | Manejo de errores estandarizado en backend (RFC 7807) |
| US-074 | Validación y sanitización de inputs (anti-XSS, anti-SQLi via ORM) |

---

## EPIC 01 — Autenticación y Autorización (Sprint 1)

| Historia | Funcionalidad |
|----------|--------------|
| US-001 | **Registro de cliente**: crear cuenta con email/contraseña, rol CLIENT automático |
| US-002 | **Login de usuario**: JWT access + refresh token, respuesta ambigua en credenciales inválidas |
| US-003 | **Refresh de token**: rotación automática, detección de replay attack |
| US-004 | **Logout**: revocación del refresh token en BD |
| US-005 | **Gestión de roles (RBAC)**: asignación por Admin, protección del último ADMIN |
| US-006 | **Protección de rutas por rol**: middleware de autorización backend |
| US-073 | **Rate limiting**: 5 intentos/IP/15min en login |

---

## EPIC 02 — Navegación y Layout Base (Sprint 1)

| Historia | Funcionalidad |
|----------|--------------|
| US-075 | **Navegación por rol**: menú adaptado según el rol del usuario autenticado |
| US-076 | **Protección de rutas en frontend**: guards de navegación por auth y rol |
| US-066 | **Renovación transparente de sesión**: interceptor Axios maneja expiración del access token |
| US-067 | **Manejo de errores global en frontend**: toast/mensajes según código HTTP |

---

## EPIC 03 — Gestión de Categorías (Sprint 2)

| Historia | Funcionalidad |
|----------|--------------|
| US-007 | **Crear categoría**: raíz o subcategoría, con nombre único |
| US-008 | **Listar categorías jerárquicas**: árbol anidado con CTE recursivo (endpoint público) |
| US-009 | **Editar categoría**: nombre y jerarquía, validación anti-ciclos |
| US-010 | **Eliminar categoría (soft delete)**: solo si no tiene productos activos |

---

## EPIC 04 — Gestión de Ingredientes y Alérgenos (Sprint 2)

| Historia | Funcionalidad |
|----------|--------------|
| US-011 | **Crear ingrediente**: nombre único + flag `es_alergeno` |
| US-012 | **Listar ingredientes**: filtrable por `es_alergeno`, paginado |
| US-013 | **Editar ingrediente**: nombre y flag de alérgeno |
| US-014 | **Eliminar ingrediente (soft delete)**: deja de aparecer para nuevas asociaciones |

---

## EPIC 05 — Gestión de Productos y Catálogo (Sprint 3)

| Historia | Funcionalidad |
|----------|--------------|
| US-015 | **Crear producto**: nombre, descripción, precio (DECIMAL), stock, imagen, disponibilidad |
| US-016 | **Asociar producto a categorías**: M2M, múltiples categorías por producto |
| US-017 | **Asociar ingredientes a producto**: M2M, con flag `es_removible` para personalización |
| US-018 | **Listar productos del catálogo (público)**: filtros por categoría, nombre, disponibilidad; paginación |
| US-019 | **Ver detalle de producto**: ingredientes, alérgenos, categorías, stock > 0 |
| US-020 | **Editar producto**: precio (>0, max 2 decimales), descripción, imagen, disponibilidad |
| US-021 | **Gestionar stock**: actualizar `stock_cantidad` de forma atómica (nunca negativo) |
| US-022 | **Eliminar producto (soft delete)**: preserva datos en pedidos históricos |
| US-023 | **Filtrar productos por alérgenos**: excluir productos con ingredientes específicos |

---

## EPIC 06 — Gestión del Perfil del Cliente (Sprint 3)

| Historia | Funcionalidad |
|----------|--------------|
| US-061 | **Ver perfil propio**: nombre, email, teléfono, fecha de registro (solo propios datos) |
| US-062 | **Editar perfil propio**: nombre y teléfono. Email NO se puede cambiar. |
| US-063 | **Cambiar contraseña**: verificar actual + nueva (min 8 chars) + invalidar refresh tokens |

---

## EPIC 07 — Gestión de Direcciones de Entrega (Sprint 4)

| Historia | Funcionalidad |
|----------|--------------|
| US-024 | **Crear dirección**: calle, número, piso/depto, ciudad, CP. Primera = predeterminada automática. |
| US-025 | **Listar direcciones del cliente**: solo las propias, indicando cuál es predeterminada |
| US-026 | **Editar dirección**: solo las propias (ownership por JWT) |
| US-027 | **Eliminar dirección**: reasignar predeterminada si era la actual |
| US-028 | **Establecer dirección predeterminada**: transacción: quitar flag anterior, setear en nueva |

---

## EPIC 08 — Carrito de Compras (Sprint 4)

| Historia | Funcionalidad |
|----------|--------------|
| US-029 | **Agregar producto al carrito**: cantidad, acumula si ya existe. Persiste en localStorage. |
| US-030 | **Personalizar producto**: excluir ingredientes (solo los que el producto tiene) |
| US-031 | **Modificar cantidad**: actualizar subtotal reactivamente. Cantidad 0 = eliminar. |
| US-032 | **Eliminar ítem del carrito**: recalcula total |
| US-033 | **Ver resumen del carrito**: nombre, cantidad, precio, exclusiones, subtotal, total general |
| US-034 | **Vaciar carrito**: confirmación modal previa |

---

## EPIC 09 — Validaciones Pre-Checkout (Sprint 5)

| Historia | Funcionalidad |
|----------|--------------|
| US-069 | **Validar disponibilidad al checkout**: verificar stock y disponibilidad de cada ítem del carrito |
| US-070 | **Verificar precios actualizados**: notificar si precio cambió desde que se agregó al carrito |

---

## EPIC 10 — Creación de Pedidos (Sprint 5)

| Historia | Funcionalidad |
|----------|--------------|
| US-035 | **Crear pedido**: atómico (UoW), snapshots de precio y dirección, estado PENDIENTE inicial, vacía carrito |
| US-036 | **Validación de stock**: SELECT FOR UPDATE dentro de la transacción |
| US-037 | **Snapshot de precios**: `precio_snapshot` en DetallePedido |
| US-038 | **Snapshot de dirección**: `direccion_snapshot` en Pedido |

---

## EPIC 11 — Pagos con MercadoPago (Sprint 6)

| Historia | Funcionalidad |
|----------|--------------|
| US-045 | **Iniciar proceso de pago**: crear orden en MP con `idempotency_key`, tokenización PCI SAQ-A en browser |
| US-046 | **Procesar webhook IPN**: actualizar estado pago, disparar `PENDIENTE → CONFIRMADO` si `approved` |
| US-047 | **Consultar estado de pago**: estado, monto, fecha (solo propios pedidos) |
| US-048 | **Reintentar pago rechazado**: nuevo `idempotency_key`, pedido sigue en PENDIENTE |

---

## EPIC 12 — Máquina de Estados de Pedidos (Sprint 6)

| Historia | Funcionalidad |
|----------|--------------|
| US-039 | **PENDIENTE → CONFIRMADO**: automático por pago aprobado, decrementa stock atómicamente |
| US-040 | **CONFIRMADO → EN_PREPARACIÓN**: manual por Gestor de Pedidos |
| US-041 | **EN_PREPARACIÓN → EN_CAMINO**: manual por Gestor de Pedidos |
| US-042 | **EN_CAMINO → ENTREGADO**: manual por Gestor de Pedidos. Estado terminal. |
| US-043 | **Cancelar pedido**: restaura stock si venía de CONFIRMADO+. Estado terminal. |
| US-044 | **Auditoría de cambios de estado**: historial append-only con actor y motivo |

---

## EPIC 13 — Visualización de Pedidos (Sprint 7)

| Historia | Funcionalidad |
|----------|--------------|
| US-049 | **Ver mis pedidos (Cliente)**: listado paginado, filtro por estado, solo propios |
| US-050 | **Ver detalle de mi pedido**: ítems con snapshots, dirección, estado de pago |
| US-051 | **Ver todos los pedidos (Gestor/Admin)**: panel con filtros, búsqueda, paginación |
| US-052 | **Ver detalle de cualquier pedido**: ítems, historial, datos del cliente, pago |

---

## EPIC 14 — Notificaciones y Feedback UX (Sprint 7)

| Historia | Funcionalidad |
|----------|--------------|
| US-071 | **Confirmación de pedido creado**: pantalla de confirmación con resumen y link a pago |
| US-072 | **Feedback de estado de pago**: retorno de MercadoPago con resultado (aprobado/rechazado/pendiente) |

---

## EPIC 15 — Administración de Usuarios (Sprint 8)

| Historia | Funcionalidad |
|----------|--------------|
| US-053 | **Listar usuarios del sistema**: búsqueda por nombre/email, filtro por rol, paginación |
| US-054 | **Editar usuario (Admin)**: roles, activar/desactivar. Invalida refresh tokens del usuario modificado. |
| US-055 | **Desactivar usuario**: baja lógica. Invalida todos sus refresh tokens. |

---

## EPIC 16 — Gestión Avanzada de Catálogo (Admin) (Sprint 8)

| Historia | Funcionalidad |
|----------|--------------|
| US-064 | **CRUD catálogo completo (Admin)**: mismos permisos que STOCK |
| US-065 | **Control total sobre pedidos (Admin)**: mismos permisos que PEDIDOS |

---

## EPIC 17 — Panel de Métricas y Dashboard (Sprint 8)

| Historia | Funcionalidad |
|----------|--------------|
| US-056 | **Dashboard de métricas**: total ventas, pedidos por estado, usuarios registrados, top productos |
| US-057 | **Gráfico de ventas por período**: líneas por día/semana/mes con recharts |
| US-058 | **Top productos más vendidos**: ranking con cantidad e ingreso total (barras con recharts) |
| US-059 | **Métricas de pedidos por estado**: distribución (torta con recharts) |

---

## EPIC 18 — Configuración del Sistema (Sprint 8)

| Historia | Funcionalidad |
|----------|--------------|
| US-060 | **Configuración del sistema**: parámetros operativos (horarios, mensajes, zonas) en tabla key-value |

---

## Resumen por Prioridad

| Prioridad | Épicas |
|-----------|--------|
| **Alta** | EPIC 00–13 |
| **Media** | EPIC 14–17 |
| **Baja** | EPIC 18 |

**Total: 77 historias de usuario** organizadas en 19 épicas.

---

## Referencias Cruzadas

- → [07_flujos_principales.md](07_flujos_principales.md) — Flujos que implementan estas funcionalidades
- → [05_reglas_de_negocio.md](05_reglas_de_negocio.md) — Reglas de negocio aplicables
