from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
import enum

class PriorityEnum(str, enum.Enum):
  low = "Low",
  medium = "Medium",
  high = "High"

class StatusEnum(str, enum.Enum):
   todo = "todo",
   in_progress = "in_progress",
   done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    priority: Mapped[PriorityEnum] = mapped_column(Enum(PriorityEnum), default=PriorityEnum.medium)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum), default=StatusEnum.todo)
    attachment: Mapped[str] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="tasks")