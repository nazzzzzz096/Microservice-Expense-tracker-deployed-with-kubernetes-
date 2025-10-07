from fastapi import FastAPI
from routes import router as expense_router


app = FastAPI(title="expense-service")
app.include_router(expense_router)