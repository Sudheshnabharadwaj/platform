"""Ticket request and response schemas."""

from datetime import datetime
import uuid

from pydantic import BaseModel


class TicketCommentCreate(BaseModel):
    comment: str
    is_internal: bool = False


class TicketCommentResponse(BaseModel):
    id: uuid.UUID
    ticket_id: uuid.UUID
    user_id: uuid.UUID
    author_name: str
    author_role: str
    comment: str
    is_internal: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketAttachmentResponse(BaseModel):
    id: uuid.UUID
    ticket_id: uuid.UUID
    file_name: str
    file_url: str | None = None
    file_size: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    title: str
    description: str
    department_id: uuid.UUID | None = None
    department_name: str | None = None
    category: str = "General Support"
    sub_category: str | None = None
    priority: str = "MEDIUM"
    attachments: list[str] | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assigned_to: uuid.UUID | None = None
    resolution_notes: str | None = None


class TicketAssignRequest(BaseModel):
    employee_id: uuid.UUID


class TicketStatusRequest(BaseModel):
    status: str
    note: str | None = None


class TicketResolveRequest(BaseModel):
    resolution_notes: str


class TicketEscalateRequest(BaseModel):
    reason: str


class TicketResponse(BaseModel):
    id: uuid.UUID
    ticket_number: str
    title: str
    description: str

    requester_id: uuid.UUID
    requester_name: str
    requester_email: str

    assigned_to: uuid.UUID | None = None
    assigned_name: str | None = None
    assigned_email: str | None = None

    department_id: uuid.UUID
    department_name: str

    category: str
    sub_category: str | None = None
    priority: str
    status: str

    sla_status: str  # 'Normal', 'SLA Risk', 'SLA Breached'
    sla_remaining: str

    created_at: datetime
    updated_at: datetime
    due_at: datetime
    resolved_at: datetime | None = None
    resolution_notes: str | None = None

    escalated: bool
    escalation_reason: str | None = None

    comments: list[TicketCommentResponse] = []
    attachments: list[TicketAttachmentResponse] = []

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
