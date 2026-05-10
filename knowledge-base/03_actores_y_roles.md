# 03 — Actores y Roles

## Actores del Sistema

Food Store contempla **cinco actores** que interactúan con la plataforma de maneras distintas y complementarias.

---

### 1. Cliente (Rol: `CLIENT`)

El usuario final de la tienda. Es el actor principal del sistema.

**Capacidades:**
- Registrarse e iniciar sesión
- Navegar el catálogo de productos y ver detalle con ingredientes/alérgenos
- Filtrar productos por categoría, nombre y alérgenos
- Agregar ítems al carrito con personalización (exclusión de ingredientes)
- Crear pedidos seleccionando dirección de entrega y forma de pago
- Pagar mediante MercadoPago
- Consultar el historial de sus propios pedidos y su estado actual
- Cancelar pedidos propios en estado PENDIENTE o CONFIRMADO
- Gestionar sus direcciones de entrega (CRUD + predeterminada)
- Editar su perfil personal y cambiar contraseña

**Restricciones:**
- Solo puede ver y operar sobre sus **propios datos**. Nunca los de otros usuarios.
- El rol `CLIENT` se asigna **automáticamente** al registrarse; no puede solicitarse via request.

---

### 2. Administrador (Rol: `ADMIN`)

Posee **control total** sobre el sistema. Es el superusuario.

**Capacidades:**
- Todo lo que puede hacer `STOCK` y `PEDIDOS`
- Gestionar usuarios: crear, editar, desactivar, asignar/quitar roles
- Acceder al panel de métricas y KPIs del dashboard
- Cancelar pedidos incluso en estado `EN_PREPARACIÓN` (único rol autorizado)
- Configurar parámetros globales del sistema

**Restricciones:**
- Un ADMIN **no puede quitarse el rol ADMIN a sí mismo** si es el último administrador del sistema.

---

### 3. Gestor de Stock (Rol: `STOCK`)

Responsable de mantener actualizado el inventario y el catálogo.

**Capacidades:**
- CRUD completo de productos (crear, editar, desactivar, soft delete)
- Gestionar categorías jerárquicas
- Gestionar ingredientes y alérgenos
- Modificar `stock_cantidad` y campo `disponible` de productos

**Restricciones:**
- **Sin acceso** a pedidos, usuarios, datos financieros ni métricas.

---

### 4. Gestor de Pedidos (Rol: `PEDIDOS`)

Se encarga del flujo operativo de los pedidos.

**Capacidades:**
- Visualizar **todos** los pedidos del sistema (de todos los clientes)
- Avanzar estados en la máquina de estados FSM:
  - `CONFIRMADO → EN_PREPARACIÓN`
  - `EN_PREPARACIÓN → EN_CAMINO`
  - `EN_CAMINO → ENTREGADO`
- Cancelar pedidos en estado `PENDIENTE` o `CONFIRMADO`

**Restricciones:**
- **Sin acceso** al catálogo de productos ni gestión de usuarios.
- **No puede** cancelar pedidos en estado `EN_PREPARACIÓN` (eso es solo ADMIN).

---

### 5. Sistema (Actor Automatizado)

Representa los procesos automáticos que operan sin intervención humana.

**Responsabilidades:**
- Recibir y procesar notificaciones IPN (Instant Payment Notification) de MercadoPago
- Actualizar el estado de los pagos en la base de datos
- Disparar la transición automática `PENDIENTE → CONFIRMADO` cuando un pago es aprobado
- Gestionar la expiración y rotación de refresh tokens de autenticación

---

## Modelo RBAC — Tabla de Permisos

| Recurso / Acción | CLIENT | STOCK | PEDIDOS | ADMIN |
|------------------|:------:|:-----:|:-------:|:-----:|
| Ver catálogo público | ✅ | ✅ | ✅ | ✅ |
| Gestionar carrito | ✅ | — | — | — |
| Crear pedido | ✅ | — | — | — |
| Cancelar pedido propio (PENDIENTE/CONFIRMADO) | ✅ | — | — | — |
| Ver mis pedidos | ✅ | — | — | — |
| Ver todos los pedidos | — | — | ✅ | ✅ |
| Avanzar estado de pedidos (FSM) | — | — | ✅ | ✅ |
| Cancelar pedido EN_PREPARACIÓN | — | — | — | ✅ |
| CRUD Productos / Categorías / Ingredientes | — | ✅ | — | ✅ |
| Modificar stock y disponibilidad | — | ✅ | — | ✅ |
| Gestionar usuarios y roles | — | — | — | ✅ |
| Panel de métricas / dashboard | — | — | — | ✅ |
| Configuración del sistema | — | — | — | ✅ |

---

## Roles en la Base de Datos

Los roles son una tabla catálogo (`Rol`) con **PK semántica** (`codigo VARCHAR(20)`), según la Especificación Técnica v5.0 (documento definitivo). El documento de descripción mencionaba IDs numéricos en una versión anterior del ERD; la v5.0 los reemplaza por códigos de texto para mayor legibilidad.

| Código | Nombre | Descripción |
|--------|--------|-------------|
| `ADMIN` | Administrador | Control total del sistema |
| `STOCK` | Gestor de Stock | Gestión de catálogo e inventario |
| `PEDIDOS` | Gestor de Pedidos | Gestión del ciclo de vida de pedidos |
| `CLIENT` | Cliente | Usuario final de la tienda |

**Relación usuarios-roles:** Muchos a muchos (tabla `UsuarioRol`). Un usuario puede tener **múltiples roles simultáneamente** (por ejemplo, ADMIN + STOCK). Se aplica restricción UNIQUE compuesta `(usuario_id, rol_codigo)`.

> **Implicancia en `UsuarioRol`:** La FK es `rol_codigo VARCHAR(20)`, no `rol_id BIGINT`. El seed carga los roles con sus códigos como clave primaria explícita (`INSERT ... ON CONFLICT DO NOTHING`).

---

## Verificación de Roles en el Backend

La autorización se implementa mediante la dependencia `require_role` de FastAPI:

```python
# Endpoint que requiere solo ADMIN
@router.get("/admin/usuarios", dependencies=[Depends(require_role(["ADMIN"]))])

# Endpoint que permite ADMIN o PEDIDOS
@router.patch("/pedidos/{id}/estado", dependencies=[Depends(require_role(["ADMIN", "PEDIDOS"]))])
```

- Token inválido o ausente → HTTP **401** Unauthorized
- Token válido pero sin el rol requerido → HTTP **403** Forbidden

---

## Rutas Públicas (sin autenticación)

Las siguientes rutas son accesibles sin token:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/productos` (catálogo público)
- `GET /api/v1/productos/{id}` (detalle público)
- `GET /api/v1/categorias` (árbol de categorías)

---

## Referencias Cruzadas

- → [05_reglas_de_negocio.md](05_reglas_de_negocio.md) — Reglas de negocio por dominio
- → [07_flujos_principales.md](07_flujos_principales.md) — Flujo de autenticación
