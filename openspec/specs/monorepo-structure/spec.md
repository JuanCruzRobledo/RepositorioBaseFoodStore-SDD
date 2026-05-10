# monorepo-structure Specification

## Purpose
TBD - created by archiving change us-000-setup. Update Purpose after archive.
## Requirements
### Requirement: Backend layered structure
El backend SHALL organizar el código en cuatro capas: `domain/`, `application/`, `infrastructure/`, `presentation/`. Cada capa SHALL contener únicamente código de su responsabilidad. La capa `domain/` MUST NOT importar de las otras capas.

#### Scenario: Domain layer is framework-agnostic
- **WHEN** un módulo de `backend/app/domain/` es analizado por imports estáticos
- **THEN** no SHALL aparecer ningún import de `fastapi`, `sqlmodel`, `pydantic` ni de `backend/app/infrastructure/`

#### Scenario: Presentation layer routes only
- **WHEN** se inspecciona un archivo en `backend/app/presentation/`
- **THEN** SHALL contener routers FastAPI, schemas Pydantic de I/O, y dependencies — pero NO lógica de negocio

---

### Requirement: Frontend Feature-Sliced Design structure
El frontend SHALL organizar el código en las capas `app/`, `features/`, `entities/`, `shared/` siguiendo Feature-Sliced Design. Las capas inferiores MUST NOT importar de capas superiores.

#### Scenario: Shared layer has no upward imports
- **WHEN** se analizan los imports de `frontend/src/shared/`
- **THEN** no SHALL aparecer ningún import desde `entities/`, `features/`, ni `app/`

#### Scenario: Features compose entities and shared
- **WHEN** se inspecciona un archivo en `frontend/src/features/`
- **THEN** PUEDE importar de `entities/` y `shared/`, pero NO de otros `features/`

---

### Requirement: Convención de naming de carpetas
El proyecto SHALL usar nombres en `lowercase` con guiones (`kebab-case`) para directorios. Los archivos Python SHALL usar `snake_case`. Los archivos TypeScript/React SHALL usar `kebab-case` para utilidades y `PascalCase` para componentes.

#### Scenario: Python file naming
- **WHEN** se crea un nuevo módulo Python en cualquier capa del backend
- **THEN** el archivo SHALL tener nombre `snake_case.py` (ej. `user_repository.py`)

#### Scenario: React component naming
- **WHEN** se crea un nuevo componente React
- **THEN** el archivo SHALL tener nombre `PascalCase.tsx` (ej. `ProductCard.tsx`)

