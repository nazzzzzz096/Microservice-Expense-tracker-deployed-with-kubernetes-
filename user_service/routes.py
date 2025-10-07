from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from models import User
from schemas import UserCreate, Token
from utils import get_password_hash, verify_password, create_access_token


router = APIRouter(prefix="/users", tags=["users"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/register', response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail='Username already registered')
    hashed = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username}


@router.post('/login', response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token,'user_id':db_user.id}