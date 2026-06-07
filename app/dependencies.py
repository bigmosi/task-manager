from app.database import SessionLocal

def db_get():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

