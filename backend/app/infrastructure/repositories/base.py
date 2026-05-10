from typing import Generic, TypeVar
from uuid import UUID

from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: Session) -> None:
        self.model = model
        self.session = session

    def get_by_id(self, entity_id: UUID | int) -> T | None:
        return self.session.get(self.model, entity_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> list[T]:
        statement = select(self.model).offset(offset).limit(limit)
        return list(self.session.exec(statement).all())

    def add(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        self.session.delete(entity)
