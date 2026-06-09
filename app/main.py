from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time
import logging

from app.database import engine, Base
from app import models
from app.routers import auth, users, tasks
from app.exceptions import (
    UserNotFoundException,
    TaskNotFoundException,
    NotAuthorizeException,
    DuplicateEntryException
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="A production-ready task management api built with FastApi",
    version="1.0.0"
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.exception_handler(TaskNotFoundException)
async def task_not_found(request: Request, exc: TaskNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {exc.task_id} not found"}
    )

@app.exception_handler(UserNotFoundException)
async def user_not_found(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": f"User {exc.user_id} not found"}
    )

@app.exception_handler(NotAuthorizeException)
async def not_authorized(request: Request, exc: NotAuthorizeException):
    return JSONResponse(
        status_code=403,
        content={"error": exc.message}
    )

@app.exception_handler(DuplicateEntryException)
async def duplicate_entry(request: Request, exc: DuplicateEntryException):
    return JSONResponse(
        status_code=400,
        content={"error": f"A record with this {exc.field} already exist"}
    )

@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    logger.error(f"Un handled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An un expected error occurred"}
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/", tags=["Root"])
def Root():
    return {
       "message": "Task manager API is running",
       "docs": "/docs",
       "verson": "1.0.0"
    }