from sqlalchemy import Date, ForeignKey, SmallInteger
from datetime import date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
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
    height_cm: Mapped[Optional[int]] = mapped_column(nullable=True)
    weight_kg: Mapped[Optional[int]] = mapped_column(nullable=True)
    activity_level_id: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        ForeignKey("activity_levels.id"),   
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    activity_level: Mapped["ActivityLevel"] = relationship(
        "ActivityLevel", 
        back_populates="user_profiles"
    )
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, name='{self.name}')>"