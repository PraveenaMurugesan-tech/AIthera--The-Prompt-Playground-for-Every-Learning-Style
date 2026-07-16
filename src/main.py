"""Application entrypoint for AIthera.

Creates the FastAPI application, configures middleware, mounts routers,
and exposes simple health endpoints. Designed to be started with:

    python -m uvicorn src.main:app --reload

Do not modify this file when running migrations; it is safe to import
as a module for local development and testing.
"""
from __future__ import annotations
from src.prompts.router import router as prompts_router

import logging
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.prompts.router import router as prompts_router
from src.explanations.router import router as explanations_router
from src.council_responses.router import router as council_responses_router
from src.consensus_results.router import router as consensus_results_router
from src.workflow.router import router as workflow_router


# Application metadata
APP_TITLE = "AIthera API"
APP_DESCRIPTION = "AIthera — The Prompt Playground API"
APP_VERSION = "0.1.0"


def _get_allowed_origins() -> List[str]:
    """Return a list of allowed CORS origins.

    The environment variable `FRONTEND_ORIGINS` may contain a comma-separated
    list of origins for development. Sensible localhost defaults are provided
    to enable frontend development without extra configuration.
    """

    env = os.getenv("FRONTEND_ORIGINS")
    if env:
        return [o.strip() for o in env.split(",") if o.strip()]
    # Default development origins
    return [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("aithera")

    app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=APP_VERSION)

    # Configure CORS to allow common localhost origins used in development.
    allowed_origins = _get_allowed_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router)
    app.include_router(prompts_router)
    app.include_router(explanations_router)
    app.include_router(council_responses_router)
    app.include_router(consensus_results_router)
    app.include_router(workflow_router)

    @app.on_event("startup")
    async def _startup_event() -> None:
        logger.info("Starting %s (version=%s)", APP_TITLE, APP_VERSION)
        logger.info("CORS allowed origins: %s", allowed_origins)

    # Root health endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        """Basic root endpoint used as a quick smoke check."""

        return {"message": "AIthera API is running"}

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health() -> dict:
        """Return a minimal health response that can be used by orchestration."""

        return {"status": "healthy"}

    return app


app: FastAPI = create_app()


if __name__ == "__main__":
    # Support running directly for local debugging (uvicorn preferred).
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)