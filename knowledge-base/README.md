# 🍔 Food Store — Base de Conocimiento

Base de conocimiento generada a partir de los documentos del proyecto: `Descripcion.docx`, `Historias de Usuario.docx` e `integrador.docx` (Especificación Técnica v5.0).

---

## Índice de Archivos

| Archivo | Contenido |
|---------|-----------|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito del sistema, objetivos por actor, alcance v5.0 |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack tecnológico, arquitectura backend y frontend, API REST |
| [03_actores_y_roles.md](03_actores_y_roles.md) | 5 actores del sistema, tabla RBAC completa, rutas públicas |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | ERD v5 completo: 3 dominios, todas las entidades y relaciones, seed data |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | ~50 reglas codificadas por dominio (RN-AU, RN-RB, RN-CA, RN-PE, RN-FS, RN-PA, RN-DA) |
| [06_funcionalidades.md](06_funcionalidades.md) | 77 historias de usuario organizadas en 19 épicas |
| [07_flujos_principales.md](07_flujos_principales.md) | 7 flujos detallados: auth, catálogo, creación pedido (UoW), pago, FSM, webhook, token refresh |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones UoW/Repository, estructura de directorios, seguridad, variables de entorno |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | 17 decisiones de diseño documentadas + 10 supuestos inferidos |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | 5 inconsistencias detectadas + 10 preguntas abiertas priorizadas |

---

## Quick Start para Desarrolladores

1. **Entender el dominio** → Leer [01](01_vision_y_objetivos.md) y [03](03_actores_y_roles.md)
2. **Entender los datos** → Leer [04](04_modelo_de_datos.md)
3. **Entender las reglas** → Leer [05](05_reglas_de_negocio.md)
4. **Entender la arquitectura** → Leer [02](02_descripcion_general.md) y [08](08_arquitectura_propuesta.md)
5. **Implementar** → Seguir el orden de sprints en [07](07_flujos_principales.md) y [06](06_funcionalidades.md)
6. **Antes de codificar** → Revisar [10](10_preguntas_abiertas.md) para desambigüar

---

## Resumen Ejecutivo

**Food Store** es un e-commerce de alimentos full-stack con:
- Backend: **FastAPI + SQLModel + PostgreSQL** (arquitectura en capas, feature-first)
- Frontend: **React + TypeScript + Vite** (Feature-Sliced Design)
- Estado: **Zustand** (cliente) + **TanStack Query** (servidor)
- Pagos: **MercadoPago Checkout API** con webhooks IPN
- Auth: **JWT doble token** (access 30min + refresh 7días) con RBAC 4 roles
- Pedidos: **Máquina de estados FSM** con audit trail append-only
- Patrones clave: Unit of Work, Repository, Snapshot, Soft Delete, Idempotent Payments

---

*Generado el 2026-04-01 a partir de: Descripcion.docx.pdf · Historias de Usuario.docx.pdf · integrador.docx.pdf*
