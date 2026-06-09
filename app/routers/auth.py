from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.token import Token
from app.schemas.user import UserResponse
from app.dependencies import db_get
from app.utils import verify_password
from app.Oauth2 import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

def send_login_notification(username: str):
    # Simulate sending email notification
    print(f"Login notification sent to {username}")

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(db_get)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    background_tasks.add_task(send_login_notification, user.username)

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user