# AGENTS.md — Reglas del proyecto Food Store

Este archivo define cómo los agentes de IA deben trabajar en este repositorio. **Es la fuente de verdad** que el agente lee antes de cada acción no trivial.

---

## Stack tecnológico

**Backend**: FastAPI · SQLModel · PostgreSQL · Alembic · bcrypt · python-jose · slowapi · MercadoPago SDK
**Frontend**: React · TypeScript · Vite · TanStack Query · TanStack Form · Zustand · Axios · Tailwind CSS · Recharts

---

## Base de conocimiento

La fuente de verdad funcional vive en `knowledge-base/`:

- `01_vision_y_objetivos.md` — propósito, alcance, fuera de alcance.
- `02_descripcion_general.md` — stack y arquitectura general.
- `03_actores_y_roles.md` — actores, RBAC, rutas públicas.
- `04_modelo_de_datos.md` — entidades, ERD, seed data.
- `05_reglas_de_negocio.md` — reglas codificadas (RN-XX-NN).
- `06_funcionalidades.md` — historias de usuario por épica.
- `07_flujos_principales.md` — flujos E2E (auth, pedidos, pago, etc.).
- `08_arquitectura_propuesta.md` — patrones, estructura, seguridad.
- `09_decisiones_y_supuestos.md` — decisiones documentadas + supuestos.
- `10_preguntas_abiertas.md` — inconsistencias y preguntas pendientes.

**Antes de proponer cualquier change**, leé los archivos relevantes de la KB. Si una decisión no está documentada ahí, marcala como **Suposición:** explícita y no avances sin validación.

---

## Índice de changes

`CHANGES.md` (raíz del proyecto) es el **índice canónico** de todos los changes con dependencias, gates de paralelismo, camino crítico y nivel de governance. Antes de ejecutar `/opsx:propose` para cualquier change, **leer el `CHANGES.md` y los archivos KB listados en la sección "Leer antes" del change correspondiente**.

---

## Reglas duras

1. **No hagas build automático.** El usuario corre los builds. Vos solo escribís código.
2. **No commitees automáticamente.** Esperá pedido explícito.
3. **No mockees la base de datos en tests.** Usá una DB real (test container o similar).
4. **No agregues "Co-Authored-By" en commits.** Usá Conventional Commits puros.
5. **No re-exportes símbolos solo "por compatibilidad".** Si algo está sin uso, eliminalo.
6. **Antes de borrar archivos**, verificá referencias con grep.

---

## Convenciones

### Commits
Conventional Commits — `feat(modulo): ...`, `fix(modulo): ...`, `refactor(modulo): ...`, `docs(modulo): ...`, `test(modulo): ...`.

### Naming de changes
- kebab-case
- Prefijo `usX-NNN-` cuando mapea a una US (`us-001-auth`, `us-005-pedidos`).
- Prefijo `infra-` para changes transversales (`infra-observability`).

### Estructura backend (FastAPI)
- Capa `domain/` — entidades, value objects, reglas de negocio puras (sin imports de FastAPI ni SQLModel).
- Capa `application/` — casos de uso, orquestación, Unit of Work.
- Capa `infrastructure/` — repositorios concretos, sesiones DB, integraciones externas.
- Capa `presentation/` — routers, schemas Pydantic, dependencies.

### Estructura frontend (React)
- Feature-Sliced Design: `app/`, `features/`, `entities/`, `shared/`.
- Componentes container vs presentational explícitos.
- Estado servidor: TanStack Query. Estado cliente: Zustand.

### Tests
- Backend: pytest + DB de test real (no mocks).
- Frontend: Vitest + Testing Library + MSW para fetch.
- TDD estricto en lógica de dominio.

---

## Skills disponibles en el proyecto

| Skill | Para qué |
|-------|----------|
| `kb-creator` | Generar/regenerar la base de conocimiento. |
| `roadmap-generator` | Generar `openspec/roadmap.md` desde la KB. |
| `find-skills` | Buscar e instalar skills adicionales del marketplace. |
| `openspec-explore` (OPSX) | Pensar antes de comprometerse a un change. |
| `openspec-propose` (OPSX) | Crear proposal + design + tasks de un change. |
| `openspec-apply-change` (OPSX) | Implementar tasks de un change. |
| `openspec-archive-change` (OPSX) | Sincronizar specs y archivar el change. |

---

## Flujo de trabajo

```
/opsx:explore   →  pensar antes de comprometerse (opcional)
/opsx:propose   →  generar proposal + design + tasks
/opsx:apply     →  implementar tarea por tarea
/opsx:archive   →  sincronizar specs y cerrar
```

**Cada change se implementa de a uno.** No se mezclan changes en una misma sesión de `apply`.
