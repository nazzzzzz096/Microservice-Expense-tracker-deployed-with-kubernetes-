from pydantic import BaseModel
from datetime import date,datetime
from typing import Optional

class ExpenseCreate(BaseModel):
    category: Optional[str]=None
    amount: float
    date: date
    description: Optional[str]=None


class ExpenseOut(ExpenseCreate):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True