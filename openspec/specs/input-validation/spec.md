# input-validation Specification

## Purpose
TBD - created by archiving change us-000-setup. Update Purpose after archive.
## Requirements
### Requirement: Validación estricta de inputs en backend
Todos los endpoints SHALL aceptar input únicamente vía schemas Pydantic con `model_config = ConfigDict(extra="forbid")`. Los inputs que contengan campos no declarados SHALL ser rechazados con status 422.

#### Scenario: Campo extra rechazado
- **WHEN** un cliente envía un payload con un campo `"hacker_field": "..."` no declarado en el schema
- **THEN** la respuesta SHALL tener status 422 y mencionar el campo extra en `errors`

#### Scenario: Tipos coercionados estrictamente
- **WHEN** un cliente envía un campo declarado como `int` con valor `"abc"`
- **THEN** la respuesta SHALL tener status 422 y mencionar el campo y el tipo esperado

---

### Requirement: Prohibición de SQL crudo
El backend MUST NOT contener queries SQL crudas (`session.execute(text("SELECT ..."))` con interpolación de strings de usuario). TODA persistencia SHALL pasar por SQLModel/SQLAlchemy con queries parametrizadas.

#### Scenario: Búsqueda de auditoría estática
- **WHEN** se hace una revisión de código del backend
- **THEN** no SHALL existir uso de `text()` con strings interpolados a partir de inputs del usuario
- **AND** todas las queries SHALL usar la API de SQLModel o `select()` con bindings

---

### Requirement: Escape automático de salida en frontend
El frontend SHALL renderizar todo contenido proveniente del usuario o del backend usando los mecanismos seguros de React (JSX). MUST NOT usar `dangerouslySetInnerHTML` salvo en componentes específicos auditados.

#### Scenario: Render de descripción de producto
- **WHEN** el frontend recibe una descripción de producto que contiene `<script>alert("xss")</script>`
- **THEN** el navegador SHALL renderizar el texto literal, NO ejecutar el script

#### Scenario: Uso restringido de dangerouslySetInnerHTML
- **WHEN** un componente nuevo usa `dangerouslySetInnerHTML`
- **THEN** el componente SHALL tener un comentario que justifique el uso y referenciar el sanitizador aplicado (DOMPurify u otro)

