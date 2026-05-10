# 07 — Flujos Principales

---

## Flujo 1 — Registro y Login (Autenticación)

```
Cliente                   Frontend                    Backend (FastAPI)
   │                          │                              │
   │── POST /auth/register ──>│                              │
   │   { nombre, email, pwd } │── POST /api/v1/auth/register ──>│
   │                          │                              │── Validar email único
   │                          │                              │── Hash bcrypt(pwd)
   │                          │                              │── Crear Usuario
   │                          │                              │── Asignar rol CLIENT
   │                          │                              │── Generar access + refresh token
   │                          │<── 201 TokenResponse ────────│
   │                          │── authStore.login(tokens)    │
   │<── Redirigir a catálogo ─│                              │
```

**Flujo de login con access token expirado (renovación transparente):**
```
Axios interceptor detecta 401
   │── POST /api/v1/auth/refresh { refresh_token }
   │<── 200 TokenResponse (nuevo par)
   │── authStore.updateTokens(tokens)
   │── Reintentar request original (transparente para el usuario)
```

**Reglas aplicadas:** RN-AU01, RN-AU02, RN-AU03, RN-AU06, RN-AU07, RN-AU08

---

## Flujo 2 — Navegación del Catálogo y Carrito

```
Cliente               Frontend (Zustand + TanStack Query)
   │                           │
   │── Accede a /catalogo ────>│
   │                           │── useProductos(filtros) → GET /api/v1/productos
   │<── Lista de productos ────│   (TanStack Query: caché, paginación, skeleton)
   │
   │── Selecciona producto ───>│── GET /api/v1/productos/{id}
   │<── Detalle + ingredientes │   (ingredientes con is_alergeno, categorías)
   │
   │── Personaliza (excluye   >│── cartStore.addItem(producto, cantidad, exclusiones)
   │   ingredientes)           │   (solo ingredientes que el producto tiene: RN-CR04)
   │<── Carrito actualizado ──│    (persiste en localStorage: RN-CR01, RN-CR02)
```

**Reglas aplicadas:** RN-CA08, RN-CR01, RN-CR02, RN-CR03, RN-CR04, RN-CR05

---

## Flujo 3 — Creación de Pedido (Unit of Work)

Este es el flujo más complejo del sistema. **Todos los INSERT son atómicos.**

```
Paso | Capa      | Operación                                             | ¿Toca BD?
-----|-----------|-------------------------------------------------------|----------
 1   | Router    | Recibe POST /api/v1/pedidos                           | No
     |           | Valida body con CrearPedidoRequest                    |
 2   | Router    | with UnitOfWork() as uow:                             | No
     |           |   service.crear_pedido(uow, body, usuario_id)         |
 3   | Service   | Verifica que usuario existe y está activo              | Lectura
     |           | Verifica que direccion_id pertenece al usuario        |
 4   | Service   | Verifica que la forma_pago existe y está habilitada   | Lectura
 5   | Service   | Por cada ítem: uow.productos.get_by_id()              | Lectura
     |           | - disponible = true                                   | (SELECT
     |           | - eliminado_en IS NULL                                |  FOR UPDATE)
     |           | - stock_cantidad >= cantidad solicitada               |
     |           | Si falla → HTTPException (rollback automático)        |
 6   | Service   | Crea snapshots:                                       | No
     |           | - precio_snapshot = producto.precio_base              |
     |           | - direccion_snapshot = serializar(direccion)         |
 7   | Service   | Calcula total:                                        | No
     |           | subtotal_i = cantidad_i × precio_snapshot_i           |
     |           | total = Σ subtotal_i + costo_envio                   |
 8   | Service   | uow.pedidos.create(pedido) + uow.flush()              | INSERT + flush
     |           | → obtiene pedido.id                                   |
 9   | Service   | Por cada ítem: uow.detalles.create(detalle)           | INSERT × N
     |           | (con nombre_snapshot, precio_snapshot, personalizacion)|
10   | Service   | uow.historial.create(                                 | INSERT
     |           |   estado_desde=NULL, estado_hasta=PENDIENTE,          |
     |           |   usuario_id=usuario_id)                              |
11   | UoW       | __exit__ sin excepción → session.commit()             | COMMIT
     |           | Todo persiste atómicamente                            |
12   | Router    | Serializa con PedidoRead.model_validate(pedido)       | No
     |           | Retorna HTTP 201                                      |
ERR  | UoW       | Si cualquier paso 3-10 lanza excepción →              | ROLLBACK
     |           | __exit__ llama rollback(). Nada persiste.             |
```

**Reglas aplicadas:** RN-PE01 a RN-PE08, RN-FS06, RN-FS07, RN-DA06

---

## Flujo 4 — Proceso de Pago con MercadoPago

```
Frontend (React)          Backend (FastAPI)           MercadoPago
     │                          │                          │
     │── Renderiza <CardPayment>│                          │
     │   (SDK MP tokeniza)      │                          │
     │── card_token generado ──>│                          │
     │                          │                          │
     │── POST /api/v1/pagos/crear                          │
     │   { pedido_id, card_token }                         │
     │                          │── Genera idempotency_key │
     │                          │── sdk.payment.create()  ─────>│
     │                          │<── { mp_payment_id, status } ─│
     │                          │── UoW: INSERT Pago       │
     │                          │   (mp_status, idempotency_key)│
     │<── 201 PagoResponse ─────│                          │
     │── paymentStore.update()  │                          │
     │── Polling cada 30s ─────>│── GET /pedidos/{id}      │
     │                          │                          │
     │                     [Asíncrono]                     │
     │                          │<── POST /api/v1/pagos/webhook ─│
     │                          │   (IPN: topic=payment)   │
     │                          │── Verificar idempotency_key (RN-PA02)
     │                          │── GET mp.payment.get(mp_payment_id) (RN-PA04)
     │                          │── UPDATE Pago.mp_status  │
     │                          │── Si approved:           │
     │                          │   FSM: PENDIENTE→CONFIRMADO
     │                          │   Decrementar stock (RN-FS03)
     │                          │   INSERT HistorialEstadoPedido
     │                          │── Response 200 OK        │
```

**Reglas aplicadas:** RN-AU09, RN-PA01 a RN-PA09, RN-FS02, RN-FS03

---

## Flujo 5 — Avance de Estado de Pedido (FSM)

```
Gestor de Pedidos         Router                     Service
       │                     │                           │
       │── PATCH /api/v1/pedidos/{id}/estado             │
       │   { nuevo_estado: "EN_PREPARACION",             │
       │     motivo: "..." }  │                           │
       │                     │── Valida rol PEDIDOS/ADMIN│
       │                     │── service.avanzar_estado()│
       │                     │                           │── Carga pedido actual
       │                     │                           │── Valida: es_terminal = false (RN-FS06)
       │                     │                           │── Valida: transición en mapa FSM (RN-FS01)
       │                     │                           │── Valida: actor tiene permiso para esta transición
       │                     │                           │── UoW: UPDATE Pedido.estado_codigo
       │                     │                           │── UoW: INSERT HistorialEstadoPedido (RN-FS07)
       │                     │                           │── Si CANCELADO y venía de CONFIRMADO+:
       │                     │                           │   Restaurar stock (RN-FS05)
       │                     │<── 200 PedidoRead ────────│
       │<── Pedido actualizado│                          │
```

**Reglas aplicadas:** RN-FS01, RN-FS05, RN-FS06, RN-FS07, RN-FS08, RN-FS09, RN-RB08

---

## Flujo 6 — Webhook IPN de MercadoPago

```
MercadoPago          Backend (POST /api/v1/pagos/webhook)
     │                           │
     │── POST { topic, id } ────>│
     │                           │── Responder HTTP 200 INMEDIATAMENTE (RN-PA03)
     │                           │── [Procesar asíncronamente]
     │                           │── Verificar firma/headers de MP
     │                           │── Verificar idempotency_key (RN-PA02)
     │                           │   Si ya existe → ignorar
     │                           │── GET mp.payment.get(id) (RN-PA04)
     │                           │── Buscar Pedido por external_reference (RN-PA09)
     │                           │── UPDATE Pago.mp_status
     │                           │── Switch(mp_status):
     │                           │   "approved"   → FSM PENDIENTE→CONFIRMADO (RN-PA05)
     │                           │                  Decrementar stock
     │                           │                  INSERT HistorialEstadoPedido
     │                           │   "rejected"   → Pago marcado como rechazado (RN-PA06)
     │                           │                  Pedido sigue PENDIENTE
     │                           │   "pending"    → Solo actualizar Pago (RN-PA07)
     │                           │   "in_process" → Solo actualizar Pago (RN-PA07)
     │                           │   "cancelled"  → Registrar. Evaluar cancelación pedido.
```

---

## Flujo 7 — Renovación de Refresh Token (Rotación)

```
Frontend                  Backend
   │                          │
   │── POST /api/v1/auth/refresh { refresh_token }
   │                          │── Buscar token en BD
   │                          │── Si no existe → 401
   │                          │── Si revoked_at IS NOT NULL → 401
   │                          │   + Si reuso detectado: revocar TODOS los tokens (RN-AU05)
   │                          │── Si expires_at < now() → 401
   │                          │── Revocar token actual (revoked_at = now())
   │                          │── Generar nuevo access token (30 min)
   │                          │── Generar nuevo refresh token (7 días)
   │                          │── INSERT nuevo RefreshToken en BD
   │<── 200 TokenResponse ────│
   │── authStore.updateTokens()│
```

**Reglas aplicadas:** RN-AU03, RN-AU04, RN-AU05

---

## Plan de Sprints (Orden de Implementación)

| Sprint | Épicas | Contenido |
|--------|--------|-----------|
| **Sprint 0** | EPIC 00 | Scaffolding, BD, Alembic, seed, patrones base, stores Zustand, errores |
| **Sprint 1** | EPIC 01, 02 | Auth completa (registro, login, refresh, logout, RBAC), navegación por rol |
| **Sprint 2** | EPIC 03, 04 | CRUD categorías jerárquicas e ingredientes |
| **Sprint 3** | EPIC 05, 06 | Productos y catálogo, perfil del cliente |
| **Sprint 4** | EPIC 07, 08 | Direcciones de entrega, carrito de compras |
| **Sprint 5** | EPIC 09, 10 | Validaciones pre-checkout, creación atómica de pedidos |
| **Sprint 6** | EPIC 11, 12 | Integración MercadoPago, máquina de estados completa |
| **Sprint 7** | EPIC 13, 14 | Visualización de pedidos, feedback UX |
| **Sprint 8** | EPIC 15-18 | Admin usuarios, catálogo admin, métricas/dashboard, config |

---

## Referencias Cruzadas

- → [05_reglas_de_negocio.md](05_reglas_de_negocio.md) — Reglas implementadas en cada flujo
- → [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) — Patrón UoW detallado
- → [04_modelo_de_datos.md](04_modelo_de_datos.md) — Entidades involucradas
