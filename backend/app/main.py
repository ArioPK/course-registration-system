# backend/app/main.py

from fastapi import FastAPI

# FastAPI application instance (this is what Uvicorn will run)
app = FastAPI(
    title="Course Registration System API",
    version="0.1.0",
)


# ---- View layer example (very simple) ----
@app.get("/health", tags=["health"])
def health_check():
    """
    Simple health-check endpoint to verify the app is running.

    In MVC terms, this function is part of the View layer:
    it handles HTTP and returns a response. It could delegate
    to a controller if there was more logic.
    """
    return {"status": "ok"}

