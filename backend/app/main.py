# backend/app/main.py

from fastapi import FastAPI # type: ignore

from backend.app.config.settings import settings
from backend.app.routers import auth, course
from fastapi.middleware.cors import CORSMiddleware # type: ignore

app = FastAPI(title=settings.APP_NAME)

origin = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router )
app.include_router(course.router, prefix="/api") 