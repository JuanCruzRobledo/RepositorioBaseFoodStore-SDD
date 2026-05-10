# 09 — Decisiones de Diseño y Supuestos

Este archivo documenta las decisiones técnicas y de negocio tomadas en el diseño del sistema, con su justificación, junto a los supuestos inferidos de los documentos.

---

## Decisiones de Diseño

### DEC-01 — FastAPI como framework backend

**Decisión:** Usar FastAPI en lugar de Django o Flask.  
**Justificación:** Alto rendimiento por naturaleza ASGI asíncrona, validación automática con Pydantic, generación automática de documentación OpenAPI (Swagger/ReDoc), tipado nativo con Python type hints.

---

### DEC-02 — SQLModel como ORM

**Decisión:** Usar SQLModel en lugar de SQLAlchemy puro o Django ORM.  
**Justificación:** Creada por el mismo autor de FastAPI, combina la potencia de SQLAlchemy con la validación de Pydantic en un solo modelo, reduciendo la duplicación de código y los errores de sincronización entre modelo de BD y schema de validación.

---

### DEC-03 — Arquitectura en capas con flujo unidireccional (Router→Service→UoW→Repository→Model)

**Decisión:** Separación estricta de capas con dependencias solo hacia abajo.  
**Justificación:** Testabilidad (servicios se pueden testear con mocks del UoW), mantenibilidad (cada capa tiene una responsabilidad clara), separación de concerns (lógica HTTP vs lógica de negocio vs acceso a datos).

---

### DEC-04 — Unit of Work en lugar de gestión manual de transacciones

**Decisión:** Usar el patrón UoW implementado como context manager.  
**Justificación:** Garantiza atomicidad en operaciones complejas (crear pedido involucra insertar en 3 tablas). Evita inconsistencias por errores a mitad de la operación. El commit/rollback ocurre exactamente una vez por operación de negocio.

---

### DEC-05 — Feature-First (modular vertical) en el backend

**Decisión:** Organizar el código por funcionalidad (módulos) en lugar de por tipo técnico (todos los routers juntos, todos los servicios juntos, etc.).  
**Justificación:** Facilita el onboarding de nuevos desarrolladores (todo lo de "pedidos" está en `app/modules/pedidos/`), facilita la extracción a microservicios si fuera necesario, reduce el acoplamiento entre módulos.

---

### DEC-06 — Feature-Sliced Design en el frontend

**Decisión:** Usar FSD con capas horizontales y segmentos verticales.  
**Justificación:** Previene dependencias circulares entre features, hace predecible dónde colocar cada pieza de código, facilita el trabajo en equipo (cada desarrollador puede trabajar en su feature sin afectar a otros).

---

### DEC-07 — Separación estricta Zustand (cliente) / TanStack Query (servidor)

**Decisión:** Zustand solo para estado del cliente, TanStack Query solo para datos del servidor. Nunca mezclar.  
**Justificación:** Evita los problemas clásicos de duplicación y desincronización de datos. TanStack Query maneja automáticamente caché, revalidación y refetching. Zustand maneja estado local que no tiene fuente de verdad en el servidor (carrito, sesión).

---

### DEC-08 — Carrito 100% client-side (Zustand + localStorage)

**Decisión:** El carrito no existe en el backend. Es puramente cliente.  
**Justificación:** Simplifica la arquitectura, el carrito puede persistir sin estar autenticado, no requiere sincronización con el servidor hasta el checkout. La validación real de stock ocurre en el momento de crear el pedido.

---

### DEC-09 — Snapshot Pattern en pedidos

**Decisión:** Copiar precio y datos de dirección al momento de crear el pedido.  
**Justificación:** Los precios cambian, las direcciones se modifican o eliminan. Sin snapshots, un pedido histórico mostraría el precio actual (incorrecto) o fallaría al mostrar la dirección (si fue eliminada). Los snapshots garantizan integridad histórica inmutable.

---

### DEC-10 — Soft Delete en lugar de borrado físico

**Decisión:** Marcar registros como eliminados (campo `eliminado_en`) en lugar de borrarlos.  
**Justificación:** Preserva la integridad referencial (un producto eliminado que tiene pedidos históricos no rompe la BD), permite recuperación de datos eliminados por error, trazabilidad de quién eliminó qué y cuándo, cumplimiento con regulaciones de retención de datos.

---

### DEC-11 — Audit Trail append-only en HistorialEstadoPedido

**Decisión:** La tabla `HistorialEstadoPedido` solo admite INSERT. Nunca UPDATE ni DELETE.  
**Justificación:** Provee evidencia inmutable del ciclo de vida de cada pedido. Invaluable para auditorías, resolución de disputas con clientes, análisis operativo. Si un cliente reclama que su pedido estuvo detenido, el historial tiene los timestamps exactos.

---

### DEC-12 — Integración MercadoPago con Checkout API (Orders)

**Decisión:** Usar la API de Orders de MercadoPago en lugar de otras variantes.  
**Justificación:** Soporta múltiples medios de pago con una sola integración (tarjeta, efectivo, transferencia, cuenta MP), datos de tarjeta tokenizados en browser (cumplimiento PCI DSS SAQ-A), notificaciones push via IPN (más eficiente que polling).

---

### DEC-13 — Idempotencia de pagos con `idempotency_key`

**Decisión:** Generar un UUID único por intento de pago y almacenarlo en la tabla `Pago`.  
**Justificación:** MercadoPago puede enviar múltiples webhooks para el mismo evento (si no recibió 200 a tiempo). Sin idempotencia, un cliente podría ser cobrado dos veces. La clave de idempotencia garantiza que cada pago se procese exactamente una vez.

---

### DEC-14 — PostgreSQL como base de datos

**Decisión:** PostgreSQL en lugar de MySQL, SQLite, o NoSQL.  
**Justificación:** Soporte para `INTEGER[]` (array de enteros para personalización de pedidos), Common Table Expressions (CTE) recursivas para categorías jerárquicas, robustez y madurez del ecosistema, tipos de datos avanzados, soporte completo ACID.

---

### DEC-15 — Paginación por skip/limit (o page/size)

**Decisión:** Implementar paginación en todos los endpoints de listado.  
**Justificación:** Escalabilidad, no devolver todos los registros en una sola respuesta. Las respuestas incluyen metadatos (`total`, `page`, `pages`) para que el frontend pueda construir controles de paginación.

---

### DEC-16 — RFC 7807 para respuestas de error

**Decisión:** Todos los errores siguen el estándar Problem Details for HTTP APIs.  
**Justificación:** Formato consistente y estandarizado que permite al frontend manejar errores de forma uniforme sin parseo ad-hoc. Facilita debugging y logging.

---

### DEC-17 — Costo de envío fijo en v1

**Decisión:** El costo de envío es un valor fijo (50.00) en la primera versión.  
**Justificación:** Simplificación del MVP. La lógica de cálculo de envío (por distancia, por zona, por peso) es compleja y puede implementarse en versiones futuras sin romper la arquitectura existente.

---

## Supuestos (inferidos de los documentos)

> Los supuestos son inferencias razonables a partir de los documentos. Deben ser confirmados.

| ID | Supuesto | Base de inferencia |
|----|----------|--------------------|
| **SUP-01** | El contexto es un proyecto universitario final de carrera TUP (Tecnicatura Universitaria en Programación). | El PDF del integrador menciona "Programación 4 — TUP" y "Trabajo Práctico Integrador (TPI)". |
| **SUP-02** | El sistema está pensado para un único negocio de comidas (no un marketplace). No hay gestión de vendedores ni multi-tenant. | No hay entidad "Negocio" ni "Vendedor" en el ERD. |
| **SUP-03** | Las imágenes de productos se almacenan como URLs. No hay upload directo de archivos en la v1. | El campo `imagen` es `VARCHAR` (URL). No se menciona S3 ni almacenamiento de archivos. |
| **SUP-04** | El sistema opera en Argentina, de ahí el uso de MercadoPago Argentina. | El integrador referencia `https://www.mercadopago.com.ar/developers/es`. |
| **SUP-05** | No hay sistema de notificaciones en tiempo real (WebSockets). El cliente hace polling para verificar el estado del pago. | El integrador menciona "Polling refetchInterval" en el frontend. No se menciona WebSockets. |
| **SUP-06** | El campo `personalizacion` en `DetallePedido` almacena los IDs de los ingredientes que el cliente quiere **excluir** (no incluir). | Los documentos son consistentes en describir el carrito como "exclusión de ingredientes". |
| **SUP-07** | Un pedido con `direccion_id = NULL` representa retiro en local. | El integrador especifica: "`NULL = retiro en local (válido)`". |
| **SUP-08** | La primera dirección registrada por un cliente se marca automáticamente como predeterminada. | Regla RN-DI01: "La primera se marca como predeterminada automáticamente". |
| **SUP-09** | El test con tarjeta sandbox de MercadoPago es suficiente para demostrar la integración en la entrega. No se requiere pago real. | El integrador incluye tarjetas de prueba Sandbox y menciona que el evaluador verificará el flujo end-to-end. |
| **SUP-10** | El campo `apellido` forma parte del modelo de Usuario en la especificación v5.0 aunque no aparezca explícitamente en el ERD textual de la descripción. | El integrador v5.0 lo incluye en `RegisterRequest` y `UserResponse`. |

---

## Decisiones de Resolución de Inconsistencias

Las siguientes decisiones fueron tomadas para resolver las inconsistencias detectadas entre los tres documentos de origen. Se adoptó siempre el documento más reciente y técnicamente sólido (**Especificación Técnica v5.0 — integrador.docx**).

### DEC-18 — bcrypt cost factor: se adopta ≥ 12

**Decisión:** Usar `cost factor = 12` (configuración de Passlib: `CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)`).  
**Justificación:** El integrador v5.0 (documento más reciente) especifica ≥ 12. Es más seguro que el valor 10 mencionado en la descripción general. El costo adicional de cómputo (~250ms) es aceptable en el endpoint de login y registros de usuario, que no son operaciones de alta frecuencia.

---

### DEC-19 — Roles con PK semántica `VARCHAR(20)`

**Decisión:** La tabla `Rol` usa `codigo VARCHAR(20)` como PK. La tabla `UsuarioRol` usa `rol_codigo VARCHAR(20)` como FK, no `rol_id BIGINT`.  
**Justificación:** El ERD v5.0 (documento definitivo) establece explícitamente la PK semántica. Hace el código más legible (`"ADMIN"` en lugar de `1`), reduce joins, y elimina la posibilidad de confundir IDs entre tablas. La desventaja de mayor tamaño de FK es negligible a la escala de este sistema.

---

### DEC-20 — Campo `apellido` incluido en modelo `Usuario`

**Decisión:** `apellido VARCHAR NN` se agrega al modelo `Usuario` con validación mínimo 2, máximo 80 caracteres.  
**Justificación:** El integrador v5.0 lo incluye explícitamente en `RegisterRequest` y `UserResponse`. Es el documento de mayor peso técnico. Se prioriza sobre la descripción general que omitía el campo.

---

### DEC-21 — Ruta canónica del webhook: `POST /api/v1/pagos/webhook`

**Decisión:** La ruta oficial del endpoint de webhooks IPN es `POST /api/v1/pagos/webhook`.  
**Justificación:** Dos de los tres documentos coinciden en esta ruta. Además, respeta la convención global del sistema (`/api/v1` como prefijo). La variante `/api/webhooks/mercadopago` de las HU rompe el prefijo y se descarta. Esta URL debe configurarse en `MP_NOTIFICATION_URL`.

---

### DEC-22 — `direccion_snapshot` como campo JSONB

**Decisión:** El campo `direccion_snapshot` en la tabla `Pedido` es de tipo `JSONB` con la siguiente estructura:
```json
{
  "calle": "string",
  "numero": "string",
  "piso": "string | null",
  "departamento": "string | null",
  "ciudad": "string",
  "codigo_postal": "string",
  "referencia": "string | null"
}
```
**Justificación:** JSONB en PostgreSQL permite consultas sobre el contenido del JSON si fuera necesario (filtros futuros), es más eficiente que TEXT serializado, y es más flexible que columnas individuales (no requiere migración si se agrega un campo a la dirección). La alternativa de columnas explícitas (`direccion_calle`, `direccion_numero`, etc.) inflaría el esquema de `Pedido` y acoplaría la estructura del pedido a la de `DireccionEntrega`.

---

## Referencias Cruzadas

- → [10_preguntas_abiertas.md](10_preguntas_abiertas.md) — Puntos sin confirmar que requieren clarificación
- → [05_reglas_de_negocio.md](05_reglas_de_negocio.md) — Reglas que implementan estas decisiones
