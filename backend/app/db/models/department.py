"""Department ORM model."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Department model representing organization units (IT Support, HR, Finance, etc.)."""

    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="department",
        lazy="selectin",
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="department",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"
