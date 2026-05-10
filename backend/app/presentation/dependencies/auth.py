"""
Placeholders de autenticacion. La implementacion real vive en us-001-auth.
Cualquier endpoint que dependa de estas funciones antes de us-001-auth
levantara NotImplementedError de forma intencional.
"""
from __future__ import annotations


def get_current_user() -> None:
    raise NotImplementedError(
        "get_current_user se implementa en el change us-001-auth"
    )


def require_role(*roles: str):
    def _dependency() -> None:
        raise NotImplementedError(
            f"require_role({roles}) se implementa en el change us-001-auth"
        )

    return _dependency
