import uuid
from sqlalchemy import (
    SmallInteger, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import Base

class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4  # Добавляем генератор по умолчанию
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    goal_id: Mapped[int] = mapped_column(SmallInteger)
    formula_used: Mapped[str]
    input_data: Mapped[dict] = mapped_column(JSONB)
    results: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Добавляем обратную связь
    user: Mapped["User"] = relationship("User", back_populates="calculations")