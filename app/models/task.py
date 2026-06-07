from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
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

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False),
    description = Column(String, nullable=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)
    status = Column(Enum(StatusEnum), default=StatusEnum.todo)
    attachment = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="tasks")