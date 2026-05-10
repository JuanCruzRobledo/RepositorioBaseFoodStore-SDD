# 05 — Reglas de Negocio

Las reglas de negocio están codificadas con identificadores únicos que permiten trazarlas hasta las historias de usuario correspondientes.

---

## Dominio: Autenticación y Seguridad

| ID | Regla |
|----|-------|
| **RN-AU01** | La contraseña **NUNCA** se almacena en texto plano. Se hashea con bcrypt con **cost factor ≥ 12** y salt automático. |
| **RN-AU02** | El access token JWT tiene duración de **30 minutos**, contiene `userId`, `email` y `roles`, firmado con HS256. |
| **RN-AU03** | El refresh token tiene duración de **7 días**, es un token opaco (UUID v4 o SHA-256) almacenado en BD. |
| **RN-AU04** | Al usar un refresh token se aplica **rotación**: el anterior se revoca y se emite uno nuevo. |
| **RN-AU05** | Si se detecta reuso de un refresh token ya utilizado (**replay attack**), se revocan **TODOS** los tokens del usuario. |
| **RN-AU06** | Rate limiting en login: máximo **5 intentos por IP** en ventana de **15 minutos**. Excedido retorna HTTP 429. |
| **RN-AU07** | Al registrarse se asigna automáticamente el rol `CLIENT`. El rol **NO** viene del request. |
| **RN-AU08** | La respuesta de login **NO** debe diferenciar "email no existe" de "contraseña incorrecta" (seguridad contra enumeración). |
| **RN-AU09** | Los datos sensibles de tarjetas **NUNCA** pasan por el servidor de Food Store (PCI DSS SAQ-A). La tokenización ocurre en el browser via SDK de MercadoPago.js. |
| **RN-AU10** | El archivo `.env` con secrets **NUNCA** se commitea al repositorio. |

---

## Dominio: Autorización y Roles (RBAC)

| ID | Regla |
|----|-------|
| **RN-RB01** | Existen 4 roles fijos: `ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT`. |
| **RN-RB02** | Un usuario puede tener **múltiples roles simultáneamente** (M2M con restricción UNIQUE compuesta). |
| **RN-RB03** | Solo `ADMIN` puede asignar/modificar roles de otros usuarios. |
| **RN-RB04** | Un ADMIN **no puede quitarse el rol ADMIN a sí mismo** si es el último administrador del sistema. |
| **RN-RB05** | Un `CLIENT` solo puede ver y operar sobre sus **propios datos**, nunca los de otros usuarios. |
| **RN-RB06** | `Gestor de Stock` **NO** tiene acceso a pedidos, usuarios ni métricas. |
| **RN-RB07** | `Gestor de Pedidos` **NO** tiene acceso al catálogo ni gestión de usuarios. |
| **RN-RB08** | Solo `ADMIN` puede cancelar pedidos en estado `EN_PREPARACIÓN`. |
| **RN-RB09** | Si el usuario no posee el rol requerido, el sistema retorna HTTP **403 Forbidden**. |
| **RN-RB10** | Endpoint sin token válido retorna HTTP **401**. Rutas públicas (catálogo, login, registro) no requieren auth. |

---

## Dominio: Catálogo de Productos

| ID | Regla |
|----|-------|
| **RN-CA01** | Las categorías soportan jerarquía de profundidad arbitraria mediante FK autoreferencial (`padre_id`). |
| **RN-CA02** | **No** se permite asignar una categoría como padre de sí misma ni generar ciclos en la jerarquía. |
| **RN-CA03** | **No** se puede eliminar una categoría que tenga productos activos asociados. |
| **RN-CA04** | El precio del producto se almacena como `NUMERIC`/`DECIMAL(10,2)` de precisión fija (**nunca** float/double). |
| **RN-CA05** | El stock es un entero `>= 0`. **Nunca** puede ser negativo. |
| **RN-CA06** | Un producto puede pertenecer a **múltiples categorías** (M2M via `ProductoCategoria`). |
| **RN-CA07** | Un producto puede tener **múltiples ingredientes** (M2M via `ProductoIngrediente`). Cada ingrediente tiene flag `es_alergeno`. |
| **RN-CA08** | El catálogo público solo muestra productos con `disponible = true` y `eliminado_en IS NULL`. |
| **RN-CA09** | El soft delete marca `eliminado_en` con timestamp. **NUNCA** se borra físicamente (preserva integridad referencial con pedidos históricos). |
| **RN-CA10** | Los endpoints de admin pueden incluir parámetro `incluir_eliminados` para ver registros borrados lógicamente. |

---

## Dominio: Direcciones de Entrega

| ID | Regla |
|----|-------|
| **RN-DI01** | Un cliente puede tener **múltiples direcciones**. La primera se marca como predeterminada automáticamente. |
| **RN-DI02** | Solo **una dirección** puede ser predeterminada a la vez por usuario. |
| **RN-DI03** | Un cliente solo puede ver/editar/eliminar **sus propias** direcciones (ownership verificado por `userId` del JWT). |

---

## Dominio: Carrito de Compras

| ID | Regla |
|----|-------|
| **RN-CR01** | El carrito es **client-side only** (Zustand + localStorage). **No existe** en el backend. |
| **RN-CR02** | El carrito **persiste** al cerrar el navegador, refresh de página, y logout/login. |
| **RN-CR03** | Si un producto ya está en el carrito y se agrega de nuevo, se **incrementa la cantidad** (no se duplica). |
| **RN-CR04** | Solo se pueden excluir ingredientes que el producto **efectivamente tiene** asociados. |
| **RN-CR05** | La personalización (exclusión de ingredientes) se almacena como array de IDs de ingredientes. |

---

## Dominio: Pedidos — Creación

| ID | Regla |
|----|-------|
| **RN-PE01** | La creación de un pedido es **ATÓMICA** (Unit of Work): si falla cualquier parte, no se persiste nada. |
| **RN-PE02** | Al crear un pedido se genera **snapshot del precio** de cada producto (`precio_snapshot` en `DetallePedido`). |
| **RN-PE03** | Al crear un pedido se genera **snapshot de la dirección** de entrega (`direccion_snapshot` en `Pedido`). |
| **RN-PE04** | Se debe validar stock suficiente **DENTRO** de la transacción (idealmente con `SELECT FOR UPDATE`) antes de crear el pedido. |
| **RN-PE05** | Si algún producto no tiene stock suficiente, **no se crea NINGÚN ítem** del pedido (todo o nada). |
| **RN-PE06** | Todo pedido nace en estado `PENDIENTE` con registro inicial en `HistorialEstadoPedido`. |
| **RN-PE07** | La personalización se almacena como `INTEGER[]` (array de PostgreSQL) en `DetallePedido`. |
| **RN-PE08** | `total del pedido = suma de subtotales (cantidad × precio_snapshot) + costo de envío`. |

---

## Dominio: Pedidos — Máquina de Estados (FSM)

| ID | Regla |
|----|-------|
| **RN-FS01** | Un pedido solo puede avanzar al **siguiente estado** en la secuencia definida. No se permiten saltos ni retrocesos. |
| **RN-FS02** | La transición `PENDIENTE → CONFIRMADO` es **EXCLUSIVAMENTE automática** (por pago aprobado). Ningún usuario puede ejecutarla manualmente. |
| **RN-FS03** | Al confirmar (`PENDIENTE → CONFIRMADO`), se decrementa **atómicamente** el stock de cada producto del pedido. |
| **RN-FS04** | Si el decremento de stock falla para **cualquier** producto, toda la operación se revierte (rollback). |
| **RN-FS05** | Al cancelar un pedido que ya fue `CONFIRMADO`, se debe **restaurar el stock** de forma atómica (operación inversa de RN-FS03). |
| **RN-FS06** | `ENTREGADO` y `CANCELADO` son **estados terminales**. No se permite ninguna transición adicional desde ellos. |
| **RN-FS07** | Todo cambio de estado se registra en `HistorialEstadoPedido` (**append-only**: solo INSERT, nunca UPDATE ni DELETE). |
| **RN-FS08** | Cancelación posible desde: `PENDIENTE` (Cliente/Gestor/Admin), `CONFIRMADO` (Gestor/Admin), `EN_PREPARACIÓN` (solo Admin). |
| **RN-FS09** | Cada registro de historial incluye: estado anterior, estado nuevo, timestamp, usuario o `SISTEMA`, observación/motivo. |

### Mapa de Transiciones Válidas

| Estado Actual | Transiciones Permitidas | Actor |
|--------------|------------------------|-------|
| `PENDIENTE` | → `CONFIRMADO` | Sistema (auto, pago aprobado) |
| `PENDIENTE` | → `CANCELADO` | Cliente / Gestor de Pedidos / Admin |
| `CONFIRMADO` | → `EN_PREPARACIÓN` | Gestor de Pedidos / Admin |
| `CONFIRMADO` | → `CANCELADO` | Gestor de Pedidos / Admin (con restauración de stock) |
| `EN_PREPARACIÓN` | → `EN_CAMINO` | Gestor de Pedidos / Admin |
| `EN_PREPARACIÓN` | → `CANCELADO` | **Solo Admin** (con restauración de stock) |
| `EN_CAMINO` | → `ENTREGADO` | Gestor de Pedidos / Admin |
| `ENTREGADO` | — (terminal) | — |
| `CANCELADO` | — (terminal) | — |

---

## Dominio: Pagos — MercadoPago

| ID | Regla |
|----|-------|
| **RN-PA01** | Los datos de tarjeta se tokenizan en el browser via SDK MercadoPago.js (**nunca** tocan nuestro servidor). |
| **RN-PA02** | Cada pago tiene un `idempotency_key` único. Si se recibe webhook duplicado con misma key, se **ignora**. |
| **RN-PA03** | El webhook debe responder HTTP **200** inmediatamente para evitar reintentos de MercadoPago. |
| **RN-PA04** | Siempre se verifica el estado real **consultando la API de MercadoPago**. Nunca se confía solo en los datos del webhook. |
| **RN-PA05** | Pago `approved` → transición automática `PENDIENTE → CONFIRMADO` + decremento de stock. |
| **RN-PA06** | Pago `rejected` → pedido permanece `PENDIENTE`. El cliente puede reintentar con otro método. |
| **RN-PA07** | Pago `pending`/`in_process` → se actualiza estado del pago pero el pedido sigue `PENDIENTE`. |
| **RN-PA08** | Un pedido puede tener **múltiples intentos de pago** (relación 1:N `Pedido → Pago`). |
| **RN-PA09** | Se usa `external_reference` para vincular la preferencia de MercadoPago con el pedido en Food Store. |

---

## Dominio: Datos e Integridad

| ID | Regla |
|----|-------|
| **RN-DA01** | Todas las tablas principales tienen campos de auditoría: `creado_en` (default NOW) y `actualizado_en` (auto-update). |
| **RN-DA02** | Los IDs de seed (Roles, EstadoPedido) son **estables** y explícitos. Se referencian en el código. |
| **RN-DA03** | El script de seed es **idempotente**: ejecutarlo múltiples veces no duplica datos. |
| **RN-DA04** | El email del usuario tiene restricción `UNIQUE` e índice para optimizar búsquedas en login. |
| **RN-DA05** | `HistorialEstadoPedido` es **append-only**: NUNCA se actualiza ni se elimina un registro. |
| **RN-DA06** | Los snapshots garantizan **inmutabilidad**: cambios futuros en productos/direcciones NO afectan pedidos existentes. |
| **RN-DA07** | La paginación usa `skip/limit` (o `page/size`) con total de registros para que el frontend construya controles. |
| **RN-DA08** | Los errores de API siguen el estándar **RFC 7807** (Problem Details for HTTP APIs). |

---

## Referencias Cruzadas

- → [07_flujos_principales.md](07_flujos_principales.md) — Flujos que implementan estas reglas
- → [04_modelo_de_datos.md](04_modelo_de_datos.md) — Estructura de datos que soporta estas reglas
- → [10_preguntas_abiertas.md](10_preguntas_abiertas.md) — Ambigüedades identificadas
