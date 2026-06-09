from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.dependencies import db_get
from app.Oauth2 import get_current_user
from app.utils import hash_password
from app.exceptions import DuplicateEntryException, UserNotFoundException

router = APIRouter(prefix="/users", tags=["Users"])

def send_welcome_email(username: str, email: str):
    print(f"Welcome {username}! Email sent to {email}")

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db_get)
):
    existing = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing:
        raise DuplicateEntryException(field="username or email")

    user_data = user.dict()
    user_data["password"] = hash_password(user_data["password"])

    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(send_welcome_email, new_user.username, new_user.email)

    return new_user

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(db_get)
):
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(db_get)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundException(user_id=user_id)
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated: UserUpdate,
    db: Session = Depends(db_get),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update another user's account"
        )
    for key, value in updated.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(db_get),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's account"
        )
    db.delete(current_user)
    db.commit()
    return None