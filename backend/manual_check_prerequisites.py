# backend/manual_check_prerequisites.py (temporary)

from backend.app.database import SessionLocal
from backend.app.models.course import Course
from backend.app.models.course_prerequisite import CoursePrerequisite

def main():
    db = SessionLocal()
    try:
        c1 = db.query(Course).filter(Course.code == "CS101").first()
        c2 = db.query(Course).filter(Course.code == "CS100").first()

        if not c1 or not c2:
            print("Create CS101 and CS100 first (or seed them).")
            return

        link = CoursePrerequisite(course_id=c1.id, prereq_course_id=c2.id)
        db.add(link)
        db.commit()

        db.refresh(c1)
        print("CS101 prerequisites:", [c.code for c in c1.prerequisites])
    finally:
        db.close()

if __name__ == "__main__":
    main()
