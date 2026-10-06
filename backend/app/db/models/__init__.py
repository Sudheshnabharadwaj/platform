"""Export all ORM models for SQLAlchemy and Alembic autogenerate."""

from app.db.models.department import Department
from app.db.models.notification import Notification
from app.db.models.ticket import Ticket
from app.db.models.ticket_attachment import TicketAttachment
from app.db.models.ticket_comment import TicketComment
from app.db.models.user import User

__all__ = [
    "Department",
    "Notification",
    "Ticket",
    "TicketAttachment",
    "TicketComment",
    "User",
]
