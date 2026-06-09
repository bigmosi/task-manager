from fastapi import (APIRouter, Depends, HTTPException, status, UploadFile, File, Query)
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os

from app.models import User
from app.models.task import Task, PriorityEnum, StatusEnum
from app.schemas.task import CreateTask, TaskResponse, TaskUpdate
from app.dependencies import db_get
from app.Oauth2 import get_current_user
from app.exceptions import TaskNotFoundException, DuplicateEntryException, NotAuthorizeException


router = APIRouter(prefix="/tasks", tags=["Tasks"])

UPLOAD_DIR = "uploads/attachments"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise TaskNotFoundException(task_id=task_id)
    
    return task

def check_task_owner(task: Task, current_user: User ):
    if task.owner_id != current_user.id:
        raise NotAuthorizeException()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task:CreateTask, db: Session = Depends(db_get), current_user: User = Depends(get_current_user)):
    new_task = Task(**task.model_dump(),  owner_id = current_user.id)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
  db: Session = Depends(db_get),
  current_user: User = Depends(get_current_user),
  status: Optional[StatusEnum] = Query(None),
  priority: Optional[PriorityEnum] = Query(None),
  search:  Optional[str] = Query(None),
  skip: int = 0,
  limit: int = 10
  ):
    
   query = db.query(Task).filter(Task.owner_id == current_user.id)

   if status:
       query = query.filter(Task.status == status)

   if priority:
       query = query.filter(Task.priority == priority)

   if search:
       query = query.filter(Task.title.ilike(f"%{search}%"))
   
   return query.offset(skip).limit(limit).all()

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(db_get),
    current_user: User = Depends(get_current_user)
):
  task = get_task_or_404(task_id, db)
  check_task_owner(task, current_user)

  return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    updated: TaskUpdate,
    db: Session = Depends(db_get),
    current_user: User = Depends(get_current_user)
):
   task = get_task_or_404(task_id, db)
   check_task_owner(task, current_user)

   for key, value in updated.model_dump(exclude_unset=True).items():
       setattr(task, key, value)

   db.commit()
   db.refresh(task)

   return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(db_get),
    current_user: User = Depends(get_current_user)
):
    task = get_task_or_404(task_id, db)
    check_task_owner(task, current_user)

    db.delete(task)
    db.commit()

    return None

@router.post("/{task_id}/attachment", response_model=TaskResponse)
def upload_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(db_get),
    current_user: User = Depends(get_current_user)
):
    task = get_task_or_404(task_id, db)
    check_task_owner(task, current_user)

    allowed_types = ["image/jpeg", "image/png", "application/pdf"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not allowed"
        )
    
    file_path = os.path.join(UPLOAD_DIR, f"task_{task_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    task.attachment = file_path


    db.commit()
    db.refresh(task)

    return task