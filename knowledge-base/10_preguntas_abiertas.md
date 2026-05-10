# 10 — Preguntas Abiertas e Inconsistencias

Este archivo documenta puntos que requieren clarificación antes de implementar, y las inconsistencias detectadas entre los tres documentos de origen.

---

## ✅ Inconsistencias Resueltas

### INCON-01 — Cost Factor de bcrypt ✅ RESUELTO

| Documento | Valor |
|-----------|-------|
| Descripcion.docx.pdf | `cost factor >= 10` |
| integrador.docx.pdf (Especificación Técnica v5.0) | `cost factor >= 12` |

**Decisión:** Se adopta **cost factor ≥ 12** — valor del documento más reciente y más seguro. Aplicado en `04_modelo_de_datos.md`, `05_reglas_de_negocio.md` y `02_descripcion_general.md`.

---

### INCON-02 — Estructura de los Roles: IDs numéricos vs PK semántica ✅ RESUELTO

| Documento | Estructura |
|-----------|-----------|
| Descripcion.docx.pdf | Roles con IDs numéricos fijos: ADMIN (id=1), STOCK (id=2), etc. |
| integrador.docx.pdf (ERD v5) | Roles con `codigo VARCHAR(20)` como PK semántica |

**Decisión:** Se adopta la **PK semántica** (`codigo VARCHAR(20)`) del ERD v5.0, que es el documento definitivo de especificación. La FK en `UsuarioRol` es `rol_codigo VARCHAR(20)`. Aplicado en `03_actores_y_roles.md` y `04_modelo_de_datos.md`.

---

### INCON-03 — Nombres de los Estados del Pedido: Display vs Código de BD

| Contexto | Nombre |
|----------|--------|
| Descripcion.docx.pdf (display) | `EN_PREPARACIÓN` (con tilde) |
| integrador.docx.pdf (código BD) | `EN_PREP` |

**Aclaración (no es inconsistencia real):** Se trata de dos representaciones del mismo estado:
- **Código en BD** (`codigo VARCHAR(20)`): `EN_PREP` — sin espacios, sin tildes, identificador semántico
- **Nombre display** (`nombre VARCHAR`): `"En Preparación"` — para mostrar al usuario

Ambas coexisten en la tabla `EstadoPedido`. No es una contradicción, sino una distinción código/etiqueta.

---

### INCON-04 — Campo `apellido` en Usuario ✅ RESUELTO

| Documento | Incluye `apellido` |
|-----------|-------------------|
| Descripcion.docx.pdf (ERD) | ❌ No mencionado |
| integrador.docx.pdf (schemas) | ✅ En `RegisterRequest` y `UserResponse` |

**Decisión:** Se incluye `apellido` como campo **obligatorio** (`VARCHAR`, NN, mínimo 2 caracteres, máximo 80) en el modelo `Usuario`, siguiendo la especificación más reciente (ERD v5.0). Aplicado en `04_modelo_de_datos.md`.

---

### INCON-05 — Ruta del endpoint de webhook de MercadoPago ✅ RESUELTO

| Documento | Ruta |
|-----------|------|
| Descripcion.docx.pdf | `POST /api/v1/pagos/webhook` |
| integrador.docx.pdf | `POST /api/v1/pagos/webhook` |
| Historias de Usuario (US-046) | `POST /api/webhooks/mercadopago` ← descartada |

**Decisión:** Se adopta **`POST /api/v1/pagos/webhook`** — dos de tres documentos coinciden y respeta el prefijo global `/api/v1` del sistema. La ruta de las HU rompe la convención de prefijo y se descarta. Esta es la URL que debe configurarse en el panel de MercadoPago como `MP_NOTIFICATION_URL`. Ya estaba correctamente documentada en `07_flujos_principales.md` y `08_arquitectura_propuesta.md`.

---

## ❓ Preguntas Abiertas

### PA-01 — ¿El `apellido` es un campo obligatorio del modelo Usuario?

Las historias de usuario (US-001, US-063) no lo mencionan, pero la especificación técnica v5.0 lo incluye en los schemas. ¿Es requerido?

---

### PA-02 — ¿Cómo se calcula el costo de envío en versiones futuras?

La v1 tiene un valor fijo de `50.00`. ¿Existe algún criterio definido para futuros cálculos (por zona, por distancia, por monto mínimo de pedido)? Esto afecta la tabla `FormaPago` y la entidad `Pedido`.

---

### PA-03 — ¿La configuración del sistema (EPIC 18 / US-060) es un requisito obligatorio o deseable?

La tabla de épicas indica que EPIC 18 tiene prioridad "Baja". Sin embargo, la rúbrica no la menciona explícitamente como criterio de evaluación. ¿Es parte del entregable o es opcional?

---

### PA-04 — ¿Qué formato exacto usa `direccion_snapshot` en la tabla `Pedido`?

El documento de descripción lo describe como "copia serializada" pero no especifica si es:
- Campos explícitos en la tabla (`direccion_calle`, `direccion_numero`, etc.)
- Un campo JSON/JSONB serializado (`direccion_snapshot JSONB`)
- Un campo TEXT con JSON serializado

La especificación técnica v5.0 lista campos individuales (`direccionCalle`, `direccionNumero`, etc.) como alternativa, pero también menciona "JSON serializado en campo `direccionSnapshot`".

---

### PA-05 — ¿El soft delete aplica a `UsuarioRol` (asignaciones de roles)?

Cuando se desasigna un rol a un usuario, ¿se hace hard delete de la fila en `UsuarioRol` o soft delete? Los documentos no lo especifican explícitamente.

---

### PA-06 — ¿Existe validación de formato de teléfono específica?

Las HU mencionan "validación de formato de teléfono" pero no especifican el regex ni el formato esperado (ej: `+54 9 11 1234-5678`, `1112345678`, etc.). ¿El sistema debe manejar teléfonos internacionales?

---

### PA-07 — ¿Qué pasa con el carrito de un cliente no autenticado?

El carrito persiste en localStorage. Si un usuario navega sin estar logueado y luego se loguea, ¿se conserva el carrito anónimo o se descarta? Las HU (RN-CR02) dicen que el carrito persiste al "logout/login", lo que implica que se conserva, pero no queda claro el caso anónimo → autenticado.

---

### PA-08 — ¿El campo `motivo` en `HistorialEstadoPedido` es obligatorio SOLO para cancelaciones?

La regla RN-FS09 dice que incluye "observación opcional", pero RN-FS05 (y el schema `AvanzarEstadoRequest`) aclara que el motivo es obligatorio cuando `nuevo_estado = CANCELADO`. ¿Es obligatorio en algún otro estado?

---

### PA-09 — ¿Los endpoints de ingredientes son públicos?

El catálogo público muestra ingredientes al ver el detalle de un producto (`GET /api/v1/productos/{id}/ingredientes`). Pero ¿el listado general de ingredientes (`GET /api/v1/ingredientes`) es público o requiere autenticación?

---

### PA-10 — ¿Hay límite de ítems en el carrito / en un pedido?

Las HU no especifican un máximo de ítems distintos por pedido ni un máximo de cantidad por ítem (más allá del stock disponible). ¿Se debe implementar algún límite?

---

## 📋 Estado de Resolución

### Inconsistencias (todas resueltas)

| Estado | Ítem | Decisión tomada |
|--------|------|-----------------|
| ✅ Resuelto | INCON-01 — bcrypt cost factor | **≥ 12** (ERD v5.0, más seguro) |
| ✅ Resuelto | INCON-02 — Roles: PK numérica vs semántica | **PK semántica** `codigo VARCHAR(20)` (ERD v5.0) |
| ✅ Aclarado | INCON-03 — EN_PREPARACIÓN vs EN_PREP | No es inconsistencia: son código BD y nombre display |
| ✅ Resuelto | INCON-04 — Campo `apellido` en Usuario | **Incluir** como NN (ERD v5.0) |
| ✅ Resuelto | INCON-05 — Ruta webhook MP | **`POST /api/v1/pagos/webhook`** (dos documentos coinciden + respeta prefijo) |

### Preguntas Abiertas (pendientes de confirmación con el equipo/evaluador)

| Prioridad | Ítem | Razón |
|-----------|------|-------|
| ✅ Resuelto | PA-04 (formato direccion_snapshot) | **JSONB** con estructura definida |
| 🟡 Media | PA-07 (carrito anónimo → autenticado) | Afecta UX de checkout |
| 🟢 Baja | PA-02 (costo de envío futuro) | v1 tiene valor fijo |
| 🟢 Baja | PA-03 (EPIC 18 obligatoria) | Baja prioridad según docs |
| 🟢 Baja | PA-05 (soft delete en UsuarioRol) | Sin impacto visible en v1 |
| 🟢 Baja | PA-06 (formato teléfono) | Campo opcional |
| 🟢 Baja | PA-08 (motivo obligatorio solo en CANCELADO) | Ya documentado en RN-FS09 |
| 🟢 Baja | PA-09 (ingredientes: endpoint público) | Sin impacto en seguridad |
| 🟢 Baja | PA-10 (límite ítems en pedido) | Sin impacto en diseño base |
