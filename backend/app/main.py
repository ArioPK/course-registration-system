# backend/app/main.py

from fastapi import FastAPI # type: ignore

from backend.app.config.settings import settings
from backend.app.routers import auth, course


app = FastAPI(title=settings.APP_NAME)

app.include_router(auth.router)
app.include_router(course.router, prefix="/api") 