# error-handling Specification

## Purpose
TBD - created by archiving change us-000-setup. Update Purpose after archive.
## Requirements
### Requirement: Errores backend en formato RFC 7807
La API SHALL emitir todos los errores con `Content-Type: application/problem+json` y cuerpo conforme a RFC 7807 con los campos `type`, `title`, `status`, `detail` e `instance`.

#### Scenario: Error 404 genérico
- **WHEN** un cliente solicita un recurso que no existe
- **THEN** la respuesta SHALL tener `Content-Type: application/problem+json`
- **AND** el cuerpo SHALL incluir `"status": 404`, `"title": "Not Found"` y un `"detail"` legible

#### Scenario: Error de validación
- **WHEN** un cliente envía un payload que viola las validaciones Pydantic
- **THEN** la respuesta SHALL tener status 422
- **AND** el cuerpo SHALL incluir un campo `"errors"` con la lista de campos inválidos

#### Scenario: Error interno NO expone stack trace
- **WHEN** ocurre una excepción no manejada en un endpoint
- **THEN** la respuesta SHALL tener status 500
- **AND** el campo `"detail"` SHALL contener un mensaje genérico
- **AND** el stack trace SHALL quedar registrado en logs internos pero NO en la respuesta

---

### Requirement: Manejo global de errores frontend
El frontend SHALL tener un interceptor Axios que captura todas las respuestas con status >= 400 y dispara una notificación al usuario según el código HTTP.

#### Scenario: Error 401 dispara redirect a login
- **WHEN** el interceptor recibe una respuesta con status 401
- **THEN** SHALL limpiar el `authStore` y redirigir a `/login`

#### Scenario: Error 5xx muestra toast genérico
- **WHEN** el interceptor recibe una respuesta con status >= 500
- **THEN** SHALL mostrar un toast con el mensaje "Error del servidor. Intentá de nuevo en unos minutos."

#### Scenario: Error 4xx muestra el detail del problem+json
- **WHEN** el interceptor recibe una respuesta con status 400-499 (excepto 401)
- **THEN** SHALL mostrar un toast con el contenido del campo `detail` de la respuesta

