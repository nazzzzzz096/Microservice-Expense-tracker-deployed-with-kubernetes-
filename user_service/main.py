from fastapi import FastAPI
from routes import router as user_router


app = FastAPI(title="user-service")
app.include_router(user_router)