"""FastAPI application factory."""

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router, router as v1_router
from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.telemetry import configure_telemetry, instrument_app

settings = get_settings()

# ── Logging ──────────────────────────────────────────────────────────────────
configure_logging(debug=settings.debug)

# ── Sentry ───────────────────────────────────────────────────────────────────
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=0.2,
        profiles_sample_rate=0.1,
    )

# ── OpenTelemetry ────────────────────────────────────────────────────────────
configure_telemetry(debug=settings.debug)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ticketing Platform API",
        version="1.0.0",
        description="Ticketing Platform Backend API — FastAPI + PostgreSQL + JWT",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ───────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ──────────────────────────────────────────────────────────────
    app.include_router(v1_router)
    app.include_router(api_router)

    # ── OpenTelemetry instrumentation ─────────────────────────────────────────
    instrument_app(app)

    return app


app = create_app()
