# backend/app/main.py

from fastapi import FastAPI # type: ignore

from .config.settings import settings  # relative import from app.config

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


# Optional: basic startup log using settings
@app.on_event("startup")
async def on_startup() -> None:
    # In a real project you'd use logging instead of print()
    print(f"Starting {settings.APP_NAME} (debug={settings.DEBUG})")
