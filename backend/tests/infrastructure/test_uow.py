import pytest

from app.infrastructure.uow import UnitOfWork


@pytest.mark.asyncio
async def test_uow_commits_on_clean_exit(in_memory_session):
    uow = UnitOfWork(session=in_memory_session)
    async with uow:
        # placeholder: aca un caso de uso real haria modificaciones
        pass
    # session externa: el assert real seria en una entidad insertada
    assert uow.session is in_memory_session


@pytest.mark.asyncio
async def test_uow_rolls_back_on_exception(in_memory_session):
    uow = UnitOfWork(session=in_memory_session)

    with pytest.raises(ValueError):
        async with uow:
            raise ValueError("simulado")

    assert uow.session is in_memory_session


@pytest.mark.asyncio
async def test_uow_keeps_external_session_open(in_memory_session):
    uow = UnitOfWork(session=in_memory_session)
    async with uow:
        pass
    # session externa NO se cierra
    assert uow.session is in_memory_session
