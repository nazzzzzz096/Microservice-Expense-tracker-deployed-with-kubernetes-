from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Expense
from schemas import ExpenseCreate, ExpenseOut
from utils import get_current_user_id
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/expenses", tags=["expenses"])

security = HTTPBearer()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper to extract user_id from token
def _require_token_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    return get_current_user_id(token)

# Create new expense
@router.post("/", response_model=ExpenseOut)
def create_expense(
    expense: ExpenseCreate,
    user_id: int = Depends(_require_token_user),
    db: Session = Depends(get_db)
):
    db_exp = Expense(**expense.model_dump(), user_id=user_id)  # use token's user_id
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

# List all expenses (optionally filter by user_id)
@router.get("/", response_model=List[ExpenseOut])
def list_expenses(
    user_id_filter: Optional[int] = Query(None, alias="user_id"),
    db: Session = Depends(get_db)
):
    q = db.query(Expense)
    if user_id_filter:
        q = q.filter(Expense.user_id == user_id_filter)
    return q.order_by(Expense.date.desc()).all()

# Get single expense
@router.get("/{id}", response_model=ExpenseOut)
def get_expense(
    id: int = Path(...),
    user_id: int = Depends(_require_token_user),
    db: Session = Depends(get_db)
):
    db_exp = db.query(Expense).filter(Expense.id == id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Not found")
    if db_exp.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return db_exp

# Update an expense
@router.put("/{id}", response_model=ExpenseOut)
def update_expense(
    id: int,
    expense: ExpenseCreate,
    user_id: int = Depends(_require_token_user),
    db: Session = Depends(get_db)
):
    db_exp = db.query(Expense).filter(Expense.id == id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Not found")
    if db_exp.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    for k, v in expense.model_dump().items():
        setattr(db_exp, k, v)
    db.commit()
    db.refresh(db_exp)
    return db_exp

# Delete an expense
@router.delete("/{id}", response_model=dict)
def delete_expense(
    id: int,
    user_id: int = Depends(_require_token_user),
    db: Session = Depends(get_db)
):
    db_exp = db.query(Expense).filter(Expense.id == id).first()
    if not db_exp:
        raise HTTPException(status_code=404, detail="Not found")
    if db_exp.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(db_exp)
    db.commit()
    return {"status": "deleted"}
