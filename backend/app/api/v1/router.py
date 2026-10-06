"""Aggregate all API routes for the Ticketing Platform."""

from fastapi import APIRouter

from app.api.v1 import admin, auth, employee, health, notifications, teamlead, tickets, users

# Router without prefix (can be mounted under /api or /api/v1)
core_router = APIRouter()

core_router.include_router(health.router)
core_router.include_router(auth.router)
core_router.include_router(tickets.router)
core_router.include_router(teamlead.router)
core_router.include_router(employee.router)
core_router.include_router(admin.router)
core_router.include_router(notifications.router)
core_router.include_router(users.router)

# Prefixed routers for mounting
router = APIRouter(prefix="/api/v1")
router.include_router(core_router)

api_router = APIRouter(prefix="/api")
api_router.include_router(core_router)
