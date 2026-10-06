"""User ORM model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.department import Department
    from app.db.models.ticket import Ticket
    from app.db.models.ticket_comment import TicketComment


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Platform user supporting ADMIN, TEAM_LEAD, and EMPLOYEE roles."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="EMPLOYEE", nullable=False, index=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Optional Keycloak subject claim for SSO compatibility
    keycloak_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)

    # Relationships
    department: Mapped["Department | None"] = relationship(
        "Department",
        back_populates="users",
        lazy="selectin",
    )
    tickets_requested: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="Ticket.requester_id",
        back_populates="requester",
        lazy="selectin",
    )
    tickets_assigned: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="Ticket.assigned_to",
        back_populates="assigned_user",
        lazy="selectin",
    )
    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment",
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"
