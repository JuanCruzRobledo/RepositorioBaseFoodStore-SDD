## ADDED Requirements

### Requirement: BaseRepository genérico
El sistema SHALL exponer una clase `BaseRepository[T]` parametrizada en el tipo del modelo SQLModel, ubicada en `backend/app/infrastructure/repositories/base.py`. La clase MUST recibir el tipo del modelo y una `Session` en el constructor.

#### Scenario: Crear repositorio concreto heredando
- **WHEN** un desarrollador crea `UserRepository(BaseRepository[User])` con una sesión activa
- **THEN** la instancia SHALL tener disponibles los métodos `get_by_id`, `list`, `add`, `delete` sin código adicional

#### Scenario: get_by_id devuelve None si no existe
- **WHEN** se invoca `repo.get_by_id(uuid_inexistente)`
- **THEN** el método SHALL devolver `None` y NO levantar excepción

#### Scenario: add no commitea automáticamente
- **WHEN** se invoca `repo.add(entity)` fuera de un UnitOfWork
- **THEN** la entidad SHALL quedar agregada a la sesión pero NO persistida hasta que algo haga commit

---

### Requirement: UnitOfWork como context manager async
El sistema SHALL exponer una clase `UnitOfWork` ubicada en `backend/app/infrastructure/uow.py` que se use como context manager async (`async with`). Al salir del bloque sin excepción SHALL hacer `commit()`. Al salir con excepción SHALL hacer `rollback()`.

#### Scenario: Commit automático al salir sin error
- **WHEN** un use case ejecuta `async with UnitOfWork() as uow:` y modifica entidades dentro del bloque
- **AND** no se levanta ninguna excepción
- **THEN** los cambios SHALL persistirse en la base de datos

#### Scenario: Rollback automático al levantar excepción
- **WHEN** un use case ejecuta `async with UnitOfWork() as uow:` y dentro del bloque se levanta una excepción
- **THEN** los cambios SHALL revertirse y la excepción SHALL propagarse

#### Scenario: UoW expone repositorios como atributos
- **WHEN** un use case accede a `uow.users` dentro del bloque
- **THEN** SHALL recibir una instancia de `UserRepository` ligada a la misma sesión que el UoW
