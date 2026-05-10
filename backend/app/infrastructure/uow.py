from __future__ import annotations
from types import TracebackType

from sqlmodel import Session

from app.infrastructure.db.session import engine


class UnitOfWork:
    def __init__(self, session: Session | None = None) -> None:
        self._external_session = session is not None
        self.session: Session | None = session

    async def __aenter__(self) -> "UnitOfWork":
        if self.session is None:
            if engine is None:
                raise RuntimeError("DATABASE_URL no esta configurado")
            self.session = Session(engine)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        assert self.session is not None
        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            if not self._external_session:
                self.session.close()
                self.session = None
