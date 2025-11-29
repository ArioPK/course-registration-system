# backend/app/views/db_debug.py

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import get_db

router = APIRouter()


@router.get("/db-test", tags=["debug"])
def db_test(db: Session = Depends(get_db)):
    """
    Simple endpoint to verify DB connectivity.

    It runs 'SELECT 1' against the database and returns db_ok = true
    if the query succeeds and returns 1.
    """
    result = db.execute(text("SELECT 1")).scalar_one()
    return {"db_ok": result == 1}
