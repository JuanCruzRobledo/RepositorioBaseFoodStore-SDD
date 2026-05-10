from sqlmodel import Field, SQLModel

from app.infrastructure.repositories.base import BaseRepository


class _DummyEntity(SQLModel, table=True):
    __tablename__ = "_dummy_entity_test"
    id: int | None = Field(default=None, primary_key=True)
    name: str


class _DummyRepository(BaseRepository[_DummyEntity]):
    def __init__(self, session):
        super().__init__(_DummyEntity, session)


def test_get_by_id_returns_none_when_not_exists(in_memory_session):
    repo = _DummyRepository(in_memory_session)
    assert repo.get_by_id(99999) is None


def test_add_does_not_commit_automatically(in_memory_session):
    repo = _DummyRepository(in_memory_session)
    entity = _DummyEntity(name="x")

    repo.add(entity)

    # session no commiteada -> nuevo session veria 0 filas
    in_memory_session.rollback()
    assert repo.list() == []


def test_concrete_repo_inherits_crud_methods(in_memory_session):
    repo = _DummyRepository(in_memory_session)

    repo.add(_DummyEntity(name="a"))
    in_memory_session.commit()

    items = repo.list()
    assert len(items) == 1
    assert items[0].name == "a"
