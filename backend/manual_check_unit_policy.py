# backend/manual_check_unit_policy.py (TEMP)
from backend.app.database import SessionLocal
from backend.app.models.unit_limit_policy import UnitLimitPolicy

db = SessionLocal()
try:
    policy = db.get(UnitLimitPolicy, 1)
    print("Policy:", policy)
finally:
    db.close()
