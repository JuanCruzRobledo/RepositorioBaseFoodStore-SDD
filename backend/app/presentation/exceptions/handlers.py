"""Exception handlers globales que emiten errores en formato RFC 7807."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


PROBLEM_JSON = "application/problem+json"
log = logging.getLogger(__name__)


def _problem(
    request: Request,
    *,
    status_code: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    extra: dict[str, Any] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": str(request.url.path),
    }
    if extra:
        body.update(extra)
    return JSONResponse(content=body, status_code=status_code, media_type=PROBLEM_JSON)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem(
            request,
            status_code=exc.status_code,
            title=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            detail=str(exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _problem(
            request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation Error",
            detail="Uno o mas campos del payload son invalidos.",
            extra={"errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        log.exception("Unhandled exception at %s", request.url.path)
        return _problem(
            request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail="Ocurrio un error interno. El equipo fue notificado.",
        )
