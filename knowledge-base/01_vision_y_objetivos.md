# 01 — Visión y Objetivos

## Descripción del Proyecto

**Food Store** es una aplicación web full-stack de comercio electrónico orientada a la venta de productos alimenticios. Permite a clientes explorar un catálogo, gestionar un carrito de compras, realizar pedidos y pagar de forma segura mediante MercadoPago. Al mismo tiempo, provee herramientas administrativas para gestionar el inventario, procesar pedidos y obtener métricas del negocio.

Es un **Trabajo Práctico Integrador (TPI)** de la materia *Programación 4 — TUP*, desarrollado bajo la metodología **Spec-Driven Development (SDD)**.

---

## Propósito del Sistema

| # | Actor | Objetivo Principal |
|---|-------|-------------------|
| OBJ-01 | Cliente | Navegar el catálogo, gestionar carrito, pagar con MercadoPago y rastrear pedidos con trazabilidad completa |
| OBJ-02 | Administrador | Gestionar categorías, productos, stock y ciclo de vida de pedidos desde el panel |
| OBJ-03 | Gestor de Stock | Controlar disponibilidad y cantidad de stock de productos |
| OBJ-04 | Gestor de Pedidos | Avanzar el estado de los pedidos según la máquina de estados definida |
| OBJ-05 | Sistema | Garantizar trazabilidad completa de transiciones de estado mediante audit trail append-only |
| OBJ-06 | Sistema | Procesar y registrar pagos a través de la pasarela MercadoPago de forma atómica |

---

## Objetivos Técnicos Principales

1. **Experiencia de compra fluida y segura** para el cliente, con carrito persistente y pago integrado.
2. **Trazabilidad completa** de cada pedido desde su creación hasta su entrega, mediante máquina de estados y audit trail.
3. **Integridad del inventario** en todo momento, con decrementos/restauraciones atómicas de stock.
4. **Integración robusta con MercadoPago**, incluyendo webhooks IPN y manejo de idempotencia.
5. **Modelo de autorización granular** basado en roles (RBAC) que segrega responsabilidades operativas.
6. **Arquitectura mantenible** con separación de capas estricta tanto en backend como en frontend.

---

## Alcance — Versión 5.0

- ✅ Autenticación y autorización con JWT y RBAC (4 roles) + invalidación de refresh token en base de datos
- ✅ Catálogo de productos con categorías jerárquicas e ingredientes con campo `es_alergeno`
- ✅ Carrito de compras con persistencia mediante Zustand + localStorage
- ✅ Gestión de pedidos con máquina de estados de 6 estados y audit trail append-only
- ✅ Pasarela de pagos MercadoPago Checkout API: tarjeta de crédito/débito, Rapipago, Pago Fácil
- ✅ Notificaciones webhook IPN de MercadoPago para confirmación automática de pagos
- ✅ Módulo DireccionEntrega: CRUD completo con dirección principal por usuario
- ✅ Panel de administración: dashboard con recharts, CRUD de entidades, gestión de pedidos y stock
- ✅ Rate limiting con slowapi: máximo 5 intentos fallidos por IP en 15 minutos en el login
- ✅ CORS configurado correctamente con `CORSMiddleware` para la separación frontend/backend
- ✅ Seed data obligatorio: roles, estados de pedido, formas de pago y usuario administrador
- ✅ API REST documentada con FastAPI/OpenAPI — accesible en `/docs` y `/redoc`

---

## Fuera de Alcance (v1)

- Notificaciones en tiempo real (WebSockets / push notifications)
- Gestión de múltiples sucursales o almacenes
- Sistema de reseñas y calificaciones de productos
- Programa de fidelidad o descuentos automáticos
- Integración con otros gateways de pago (distinto de MercadoPago)

---

## Referencias Cruzadas

- → [02_descripcion_general.md](02_descripcion_general.md) — Stack tecnológico y arquitectura
- → [03_actores_y_roles.md](03_actores_y_roles.md) — Descripción detallada de actores
- → [06_funcionalidades.md](06_funcionalidades.md) — Funcionalidades por módulo
