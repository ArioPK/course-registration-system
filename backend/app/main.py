# backend/app/main.py

from fastapi import FastAPI # type: ignore
from .config.settings import settings

from .views import db_debug  # import to check if db works perfectly fine before commit 
from .routers import auth


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="0.1.0",
)


@app.get("/health", tags=["health"])
def health_check():
    """
    Simple health-check endpoint to verify the app is running.
    """
    return {"status": "ok"}


#db test router . delete later
app.include_router(db_debug.router)

# Register routers
app.include_router(auth.router)  # <-- NEW line