# backend/tests/test_factories_smoke.py

from backend.tests import factories


def test_factories_smoke(db_session, current_term):
    s = factories.make_student(db_session)
    p = factories.make_professor(db_session)
    c = factories.make_course(db_session, professor_name=p.full_name, semester=current_term)
    e = factories.add_enrollment(db_session, student_id=s.id, course_id=c.id, term=current_term)

    assert s.id is not None
    assert p.id is not None
    assert c.id is not None
    assert e is not None