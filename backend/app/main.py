# backend/app/main.py

from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore

from backend.app.config.settings import settings
from backend.app.routers import auth, course
from backend.app.routers.admin_unit_limits import router as admin_unit_limits_router
from backend.app.routers.student_courses import router as student_courses_router
from backend.app.routers.legacy_prerequisites import router as legacy_prerequisites_router


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
app.include_router(admin_unit_limits_router)
app.include_router(student_courses_router)
app.include_router(legacy_prerequisites_router)
