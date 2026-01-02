from sqlalchemy import (
    Date, ForeignKey,
)
from datetime import date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    name: Mapped[str]
    gender: Mapped[str]
    birth_date: Mapped[date]
    height_cm: Mapped[int]
    activity_level_id: Mapped[int]
    
    # Добавляем обратную связь
    user: Mapped["User"] = relationship("User", back_populates="profile")