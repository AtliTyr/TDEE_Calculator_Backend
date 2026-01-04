from sqlalchemy import SmallInteger, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class ActivityLevel(Base):
    __tablename__ = "activity_levels"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    factor: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    
    # Relationship с UserProfile (опционально)
    user_profiles: Mapped[List["UserProfile"]] = relationship(
        "UserProfile", 
        back_populates="activity_level"
    )
    
    def __repr__(self):
        return f"<ActivityLevel(id={self.id}, code='{self.code}', name='{self.name}')>"