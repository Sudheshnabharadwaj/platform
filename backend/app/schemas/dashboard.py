"""Dashboard stats schemas for Admin, Team Lead, and Employee."""

from typing import Any
from pydantic import BaseModel

from app.schemas.ticket import TicketResponse


class AdminDashboardResponse(BaseModel):
    totalTickets: int
    openTickets: int
    escalatedTickets: int
    slaRiskCount: int
    slaBreachedCount: int
    resolvedTodayCount: int
    totalUsers: int
    ticketOverview: dict[str, int]
    departmentWiseTickets: list[dict[str, Any]]
    teamWorkload: list[dict[str, Any]]
    recentTickets: list[TicketResponse]


class TeamLeadDashboardResponse(BaseModel):
    totalDepartmentTickets: int
    openTickets: int
    inProgressTickets: int
    pendingTickets: int
    resolvedTickets: int
    closedTickets: int
    escalatedTickets: int
    slaRiskCount: int
    slaBreachedCount: int
    departmentName: str
    teamMembersCount: int
    teamWorkload: list[dict[str, Any]]
    recentTickets: list[TicketResponse]


class EmployeeDashboardResponse(BaseModel):
    myCreatedTicketsCount: int
    myAssignedTicketsCount: int
    openAssignedCount: int
    inProgressAssignedCount: int
    resolvedAssignedCount: int
    slaRiskCount: int
    slaBreachedCount: int
    recentAssignedTickets: list[TicketResponse]
    recentCreatedTickets: list[TicketResponse]
