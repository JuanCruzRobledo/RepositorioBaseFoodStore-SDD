import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.exceptions.handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Food Store API", version="0.1.0")

    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
