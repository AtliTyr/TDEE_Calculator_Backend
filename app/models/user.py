import uuid
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", 
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="joined"
    )
    calculations: Mapped[list["Calculation"]] = relationship(
        "Calculation", 
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )