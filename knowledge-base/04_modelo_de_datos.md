# 04 — Modelo de Datos (ERD v5)

## Principios de Diseño

El modelo aplica:
- **Tercera Forma Normal (3FN)** — integridad referencial y mínima redundancia
- **Soft Delete** — campo `eliminado_en` / `deleted_at` (TIMESTAMPTZ nullable). Nunca se borran físicamente registros de negocio.
- **Snapshot Pattern** — precios y nombres de producto se copian al crear el pedido (inmutables)
- **Audit Trail Append-Only** — `HistorialEstadoPedido` solo admite INSERT, nunca UPDATE/DELETE
- **Campos de auditoría** — `creado_en` y `actualizado_en` en todas las tablas principales

---

## Dominio 1 — Identidad y Acceso

### Entidad: `Usuario`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | Soft-delete vía `deleted_at` |
| `nombre` | VARCHAR | NN | Mínimo 2 caracteres, máximo 80 |
| `apellido` | VARCHAR | NN | Mínimo 2 caracteres, máximo 80 (incluido en ERD v5.0) |
| `email` | VARCHAR(254) | UQ, NN | Credencial de login. Indexado. Validado con EmailStr (Pydantic v2) |
| `password_hash` | CHAR(60) | NN | bcrypt **cost factor ≥ 12**. **NUNCA** almacenar plaintext. |
| `telefono` | VARCHAR | NULL | Opcional |
| `activo` | BOOLEAN | NN, default true | false = cuenta desactivada, no puede loguearse |
| `creado_en` | TIMESTAMPTZ | NN, default NOW() | |
| `actualizado_en` | TIMESTAMPTZ | NN, auto-update | |
| `eliminado_en` | TIMESTAMPTZ | NULL | NULL = activo |

### Entidad: `Rol`

Tabla catálogo cargada por seed data. Se carga con `INSERT ... ON CONFLICT DO NOTHING` para garantizar idempotencia.

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `codigo` | VARCHAR(20) | PK (semántica) | `ADMIN`, `STOCK`, `PEDIDOS`, `CLIENT` |
| `nombre` | VARCHAR | NN | Nombre descriptivo |
| `descripcion` | TEXT | NULL | |

### Entidad: `UsuarioRol` (tabla pivot N:M)

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `usuario_id` | BIGINT | FK → Usuario, NN | |
| `rol_codigo` | VARCHAR(20) | FK → Rol, NN | |
| `asignado_por_id` | BIGINT | FK → Usuario, NULL | Admin que asignó el rol |
| PK compuesta | — | UNIQUE (usuario_id, rol_codigo) | Impide duplicados |

### Entidad: `RefreshToken`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `token_hash` | CHAR(64) | UQ, NN | SHA-256 del token. El token real se envía al cliente. |
| `usuario_id` | BIGINT | FK → Usuario, NN | |
| `expires_at` | TIMESTAMPTZ | NN | 7 días desde emisión |
| `revoked_at` | TIMESTAMPTZ | NULL | NULL = activo. Se completa en logout o rotación. |
| `creado_en` | TIMESTAMPTZ | NN | |

### Entidad: `DireccionEntrega`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `usuario_id` | BIGINT | FK → Usuario, NN | |
| `alias` | VARCHAR(50) | NULL | Ej: 'Casa', 'Trabajo' |
| `linea1` / `calle` | TEXT | NN | |
| `numero` | VARCHAR | NULL | |
| `piso` | VARCHAR | NULL | |
| `departamento` | VARCHAR | NULL | |
| `ciudad` | VARCHAR | NN | |
| `codigo_postal` | VARCHAR | NN | |
| `referencia` | TEXT | NULL | Instrucciones para el delivery |
| `es_principal` / `es_predeterminada` | BOOLEAN | NN, default false | Solo una por usuario |
| `eliminado_en` | TIMESTAMPTZ | NULL | Soft delete |

---

## Dominio 2 — Catálogo de Productos

### Entidad: `Categoria`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `nombre` | VARCHAR | NN | |
| `descripcion` | TEXT | NULL | |
| `imagen` | VARCHAR | NULL | URL de imagen |
| `padre_id` / `parent_id` | BIGINT | FK self-ref, NULL | Jerarquía recursiva. ON DELETE SET NULL. |
| `eliminado_en` | TIMESTAMPTZ | NULL | Soft delete. No se puede eliminar si tiene productos activos. |

> Las consultas jerárquicas se realizan con **Common Table Expressions (CTE) recursivas** de PostgreSQL para obtener toda la jerarquía en una sola query eficiente.

### Entidad: `Producto`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `nombre` | VARCHAR | NN | |
| `descripcion` | TEXT | NULL | |
| `imagen` | VARCHAR | NULL | URL de imagen |
| `precio_base` | DECIMAL(10,2) | CHECK ≥ 0, NN | **NUNCA** float/double. Tipo numérico de precisión fija. |
| `stock_cantidad` | INTEGER | CHECK ≥ 0, NN, default 0 | Gestionado por rol STOCK. Nunca negativo. |
| `disponible` | BOOLEAN | NN, default true | Toggle manual independiente del stock. |
| `creado_en` | TIMESTAMPTZ | NN | |
| `actualizado_en` | TIMESTAMPTZ | NN | |
| `eliminado_en` | TIMESTAMPTZ | NULL | Soft delete |

### Entidad: `Ingrediente`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `nombre` | VARCHAR(100) | UQ, NN | |
| `descripcion` | TEXT | NULL | |
| `es_alergeno` | BOOLEAN | NN, default false | Badge de alérgenos en UI |
| `eliminado_en` | TIMESTAMPTZ | NULL | |

### Tablas Pivot del Catálogo

**`ProductoCategoria`** (N:M Producto ↔ Categoria)
| Campo | Tipo | Notas |
|-------|------|-------|
| `producto_id` | BIGINT FK | |
| `cat_id` / `categoria_id` | BIGINT FK | |
| `es_principal` | BOOLEAN | Categoría principal del producto |
| PK compuesta | | (producto_id, categoria_id) |

**`ProductoIngrediente`** (N:M Producto ↔ Ingrediente)
| Campo | Tipo | Notas |
|-------|------|-------|
| `producto_id` | BIGINT FK | |
| `ingrediente_id` | BIGINT FK | |
| `es_removible` | BOOLEAN NN | Habilita personalización del pedido |
| PK compuesta | | (producto_id, ingrediente_id) |

### Entidad: `FormaPago`

Tabla catálogo cargada por seed data.

| Campo | Tipo | Notas |
|-------|------|-------|
| `codigo` | VARCHAR(20) | PK semántica: `MERCADOPAGO`, `EFECTIVO`, `TRANSFERENCIA` |
| `nombre` | VARCHAR | NN |
| `habilitado` | BOOLEAN | NN, default true. Deshabilitar sin eliminar. |

---

## Dominio 3 — Ventas, Pagos y Trazabilidad

### Entidad: `EstadoPedido`

Tabla catálogo cargada por seed data.

| Campo | Tipo | Notas |
|-------|------|-------|
| `codigo` | VARCHAR(20) | PK semántica: `PENDIENTE`, `CONFIRMADO`, `EN_PREP`, `EN_CAMINO`, `ENTREGADO`, `CANCELADO` |
| `nombre` | VARCHAR | Nombre display (con tildes, ej: "En Preparación") |
| `descripcion` | TEXT | NULL |
| `orden` | INTEGER | Orden en la secuencia lógica |
| `es_terminal` | BOOLEAN | NN. `true` = no admite transiciones salientes |

### Entidad: `Pedido`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `usuario_id` | BIGINT | FK → Usuario, NN | |
| `estado_codigo` | VARCHAR(20) | FK → EstadoPedido, NN | Estado actual |
| `direccion_id` | BIGINT | FK → DireccionEntrega, **SET NULL** | NULL = retiro en local (válido) |
| `forma_pago_codigo` | VARCHAR(20) | FK → FormaPago, NN | |
| `costo_envio` | DECIMAL(10,2) | NN, default 50.00 | Valor fijo v1. Documentado. |
| `total` | DECIMAL(10,2) | CHECK ≥ 0, NN | **Snapshot inmutable** al crear |
| `direccion_snapshot` | JSONB | NULL | Copia serializada de la dirección al momento del pedido. Formato: `{"calle": "...", "numero": "...", "piso": null, "departamento": null, "ciudad": "...", "codigo_postal": "...", "referencia": null}` |
| `notas` | TEXT | NULL | Observaciones del cliente |
| `creado_en` | TIMESTAMPTZ | NN | |
| `actualizado_en` | TIMESTAMPTZ | NN | |
| `eliminado_en` | TIMESTAMPTZ | NULL | Soft delete |

### Entidad: `DetallePedido`

Cada línea dentro de un pedido.

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `pedido_id` | BIGINT | FK → Pedido, NN | |
| `producto_id` | BIGINT | FK → Producto, NN | Referencia al producto original |
| `nombre_snapshot` | VARCHAR(200) | NN | **Snapshot** del nombre al crear. Inmutable. |
| `precio_snapshot` | DECIMAL(10,2) | NN | **Snapshot** del precio al crear. Inmutable. |
| `cantidad` | INTEGER | CHECK ≥ 1, NN | |
| `subtotal` | DECIMAL(10,2) | NN | `cantidad × precio_snapshot` |
| `personalizacion` | INTEGER[] | NULL | IDs de ingredientes removidos (array PostgreSQL) |

> El campo `personalizacion` almacena los IDs de ingredientes que el cliente desea **excluir**. El uso de `INTEGER[]` en lugar de tabla intermedia es una decisión pragmática: la personalización es inmutable y siempre se lee como un todo.

### Entidad: `HistorialEstadoPedido`

Audit trail **append-only**. NUNCA se emiten UPDATE ni DELETE sobre esta tabla.

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `pedido_id` | BIGINT | FK → Pedido, NN | |
| `estado_desde` | VARCHAR(20) | FK → EstadoPedido, **NULL** | NULL = transición inicial (primer registro) |
| `estado_hasta` | VARCHAR(20) | FK → EstadoPedido, NN | Nuevo estado |
| `usuario_id` | BIGINT | FK → Usuario, NULL | NULL si fue el Sistema automáticamente |
| `motivo` | TEXT | NULL | Obligatorio si `estado_hasta = CANCELADO` |
| `created_at` | TIMESTAMPTZ | NN | **Solo `created_at`**, nunca `updated_at` |

### Entidad: `Pago`

| Campo | Tipo | Restricción | Notas |
|-------|------|-------------|-------|
| `id` | BIGSERIAL | PK | |
| `pedido_id` | BIGINT | FK → Pedido, NN | Relación 1:N (múltiples intentos por pedido) |
| `monto` | DECIMAL(10,2) | NN | |
| `mp_payment_id` | BIGINT | UQ, **NULL** | ID devuelto por MercadoPago |
| `mp_status` | VARCHAR(30) | NN | `pending` / `approved` / `rejected` / `in_process` / `cancelled` |
| `external_reference` | VARCHAR(100) | UQ, NN | UUID del Pedido como referencia en MP |
| `idempotency_key` | VARCHAR(100) | UQ, NN | UUID generado por backend. Evita cobros duplicados. |
| `creado_en` | TIMESTAMPTZ | NN | |
| `actualizado_en` | TIMESTAMPTZ | NN | |

---

## Diagrama de Relaciones (Simplificado)

```
Usuario ──< UsuarioRol >── Rol
Usuario ──< DireccionEntrega
Usuario ──< RefreshToken
Usuario ──< Pedido

Categoria ──< Categoria (self-ref: padre_id)
Categoria >──< Producto (via ProductoCategoria)
Producto >──< Ingrediente (via ProductoIngrediente)

Pedido ──< DetallePedido
Pedido ──< HistorialEstadoPedido
Pedido ──< Pago
Pedido ── EstadoPedido (estado actual)
Pedido ── FormaPago
Pedido ── DireccionEntrega (SET NULL on delete)
DetallePedido ── Producto (referencia histórica)
```

---

## Seed Data Obligatorio

El script `seed.py` (o `python -m app.db.seed`) debe ejecutarse una vez después de `alembic upgrade head`. Sin este paso la aplicación no funciona.

| Entidad | Registros |
|---------|-----------|
| `Rol` | ADMIN, STOCK, PEDIDOS, CLIENT |
| `EstadoPedido` | PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO |
| `FormaPago` | MERCADOPAGO (habilitado), EFECTIVO (habilitado), TRANSFERENCIA (habilitado) |
| `Usuario admin` | `admin@foodstore.com` / `Admin1234!` — con rol ADMIN. Cambiar en producción. |

El script debe ser **idempotente**: `INSERT ... ON CONFLICT DO NOTHING`.

---

## Referencias Cruzadas

- → [05_reglas_de_negocio.md](05_reglas_de_negocio.md) — Reglas que aplican sobre este modelo
- → [07_flujos_principales.md](07_flujos_principales.md) — Flujo de creación de pedido (UoW)
- → [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) — Patrón Unit of Work y Repository
