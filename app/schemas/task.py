from pydantic import BaseModel, Field
from typing import Optional
from app.models.task import PriorityEnum, StatusEnum


class CreateTask(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    descripion:Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.todo

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    priority: PriorityEnum
    status: StatusEnum
    attachment: Optional[str]
    owner_id: int

    class Config:
        orm_mode = True