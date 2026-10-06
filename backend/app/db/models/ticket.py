"""Ticket ORM model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.department import Department
    from app.db.models.ticket_attachment import TicketAttachment
    from app.db.models.ticket_comment import TicketComment
    from app.db.models.user import User


class Ticket(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Ticket entity representing support requests."""

    __tablename__ = "tickets"

    ticket_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(String(100), default="General Support", nullable=False)
    sub_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Priority: LOW, MEDIUM, HIGH, CRITICAL
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False, index=True)

    # Status: OPEN, IN_PROGRESS, PENDING, RESOLVED, CLOSED
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False, index=True)

    # SLA tracking
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Escalation
    escalated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    requester: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="tickets_requested",
        lazy="selectin",
    )
    assigned_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assigned_to],
        back_populates="tickets_assigned",
        lazy="selectin",
    )
    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="tickets",
        lazy="selectin",
    )
    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketComment.created_at.asc()",
        lazy="selectin",
    )
    attachments: Mapped[list["TicketAttachment"]] = relationship(
        "TicketAttachment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_number} priority={self.priority} status={self.status}>"
