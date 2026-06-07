from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserCreate(BaseModel):
   username: str = Field(..., min_length=3, max_length=20)
   email: str
   password: str = Field(..., min_length=8)

   @field_validator("email")
   @classmethod
   def validate_email(cls, value):
      if "@" not in value:
         raise ValueError("Invalid Email")
      return value

class UserResponse(BaseModel):
   id: str
   username: str
   email: str
   is_active: bool

   class Config:
      orm_mode = True

class UserUpdate(BaseModel):
   username: Optional[str] = None
   email: Optional[str] = None