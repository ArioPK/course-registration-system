from backend.app.schemas.prerequisite import PrerequisiteCreate

print(PrerequisiteCreate(course_id=1, prereq_course_id=2))

try:
    PrerequisiteCreate(course_id=1, prereq_course_id=1)
except Exception as e:
    print("Expected error:", e)
