# Course Registration System (FastAPI + MySQL)

A multi-role **University Course Registration System**:

* **Admins** manage courses, prerequisites, and global unit-limit policy.
* **Students** browse courses, enroll/drop (scoped to the **current term**), view enrollments, and generate a weekly schedule.
* **Professors** view their current-term courses, list enrolled students, and remove students (current term only).

Backend: **FastAPI** + **SQLAlchemy** + **MySQL**, with **JWT authentication** (roles: `admin`, `student`, `professor`).

---

## Table of Contents

* [Tech Stack](#tech-stack)
* [Project Structure](#project-structure)
* [Quickstart](#quickstart)
* [Environment Variables](#environment-variables)
* [Database Setup (MySQL)](#database-setup-mysql)
* [Create Tables (No Alembic)](#create-tables-no-alembic)
* [Run the Backend](#run-the-backend)
* [Run Tests](#run-tests)
* [API Overview](#api-overview)
* [Sprint 3 Business Rules](#sprint-3-business-rules)
* [Compatibility Notes (Frontend-Friendly Shims)](#compatibility-notes-frontend-friendly-shims)
* [Contributing Workflow](#contributing-workflow)
* [Troubleshooting](#troubleshooting)

---

## Tech Stack

* **Python**: 3.10+
* **Framework**: FastAPI
* **ORM**: SQLAlchemy
* **Database**: MySQL (driver: PyMySQL)
* **Auth**: JWT (python-jose), Argon2id password hashing
* **Validation**: Pydantic (v1/v2 compatible)
* **Testing**: pytest (API tests via TestClient/httpx)

---

## Project Structure

Common folders (may vary slightly depending on your repo layout):

* `backend/app/` — FastAPI app (routers, services, models, schemas)
* `backend/tests/` — pytest test suite
* `backend/create_db.py` — creates DB tables from models
* `backend/seed_initial_admin.py` — optional dev/demo admin seeding
* `backend/requirements.txt` — dependencies
* `.env.example` — example environment config

---

## Quickstart

### 1) Create and activate a virtual environment

**Windows (PowerShell):**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3) Configure environment variables

Copy the example file to `.env` (do **not** commit `.env`):

**Windows (PowerShell):**

```bash
copy .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Then edit `.env` with your real values.

### 4) Create tables

```bash
python backend/create_db.py
```

### 5) (Optional) Seed an initial admin (dev/demo)

```bash
python backend/seed_initial_admin.py
```

### 6) Run the server

```bash
uvicorn backend.app.main:app --reload
```

Open Swagger UI:

* `http://127.0.0.1:8000/docs`

---

## Environment Variables

Your `.env.example` includes:

```env
# Database connection string (SQLAlchemy URL for MySQL + PyMySQL)
DATABASE_URL="mysql+pymysql://username:password@localhost:3306/course_registration_db"

# JWT configuration
JWT_SECRET_KEY="change_this_to_a_long_random_secret"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="30"

# General app settings
APP_NAME="Course Registration System API"
DEBUG="true"

# Initial admin seeding (dev / demo usage)
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=admin123
INITIAL_ADMIN_EMAIL=admin@example.com
INITIAL_ADMIN_NATIONAL_ID=0000000000
```

### Notes

* `DATABASE_URL` must point to an existing MySQL database.
* `JWT_SECRET_KEY` should be long and random (keep it private).
* `DEBUG=true` is for local development; in production you typically set it to `false`.
* The `INITIAL_ADMIN_*` variables are read by the seeding script.

> If your project also supports `CURRENT_TERM`, you can add it to `.env`:

```env
CURRENT_TERM="1404-1"
```

---

## Database Setup (MySQL)

You need:

* MySQL server running locally (or a remote MySQL instance)
* A database created (e.g. `course_registration_db`)
* A user with permissions

### Option A — Create DB & user (MySQL CLI)

Login as root/admin:

```sql
CREATE DATABASE course_registration_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'crs_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON course_registration_db.* TO 'crs_user'@'localhost';
FLUSH PRIVILEGES;
```

Then set your `DATABASE_URL`:

```env
DATABASE_URL="mysql+pymysql://crs_user:strong_password@localhost:3306/course_registration_db"
```

### Option B — Use an existing DB/user

Just update `DATABASE_URL` accordingly.

---

## Create Tables (No Alembic)

This project **does not use Alembic migrations**. Tables are created from SQLAlchemy models.

Run:

```bash
python backend/create_db.py
```

> Development note: if models change, you may need to drop/recreate tables (in dev only). In production, handle schema changes via manual SQL migrations.

---

## Run the Backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

* Swagger UI: `http://127.0.0.1:8000/docs`
* Base URL: `http://127.0.0.1:8000/`

---

## Run Tests

```bash
pytest -q
```

Tips:

* Use an isolated database for tests if your tests depend on `DATABASE_URL`.
* If your tests create tables automatically, ensure MySQL credentials are correct and the DB exists.

---

## API Overview

All authenticated endpoints require:

```
Authorization: Bearer <token>
```

### Auth

| Endpoint                | Method | Description                                                              |
| ----------------------- | ------ | ------------------------------------------------------------------------ |
| `/auth/login`           | POST   | Unified login `{username, password}` (tries admin → student → professor) |
| `/auth/student/login`   | POST   | Student login                                                            |
| `/auth/professor/login` | POST   | Professor login                                                          |
| `/auth/me`              | GET    | Current admin                                                            |
| `/auth/student/me`      | GET    | Current student                                                          |
| `/auth/professor/me`    | GET    | Current professor                                                        |

### Admin

| Endpoint                                      | Method         | Description                     |
| --------------------------------------------- | -------------- | ------------------------------- |
| `/api/courses`                                | GET/POST       | List / create courses           |
| `/api/courses/{id}`                           | GET/PUT/DELETE | Read / update / delete a course |
| `/api/courses/{id}/prerequisites`             | GET/POST       | List / add prerequisites        |
| `/api/courses/{id}/prerequisites/{prereq_id}` | DELETE         | Remove prerequisite             |
| `/api/admin/unit-limits`                      | GET/PUT        | Read / update unit limits       |

### Student

| Endpoint                               | Method | Description                                |
| -------------------------------------- | ------ | ------------------------------------------ |
| `/api/student/courses`                 | GET    | Browse catalog                             |
| `/api/student/enrollments`             | POST   | Enroll (accepts `course_id` or `courseId`) |
| `/api/student/enrollments`             | GET    | List current-term enrollments              |
| `/api/student/enrollments/{course_id}` | DELETE | Drop course                                |
| `/api/student/schedule`                | GET    | Weekly schedule                            |

### Professor

| Endpoint                                            | Method | Description                                   |
| --------------------------------------------------- | ------ | --------------------------------------------- |
| `/api/professor/courses`                            | GET    | Professor’s courses (current term)            |
| `/api/professor/courses/{id}/students`              | GET    | Enrolled students                             |
| `/api/professor/courses/{id}/students/{student_id}` | DELETE | Remove student enrollment (current term only) |

---

## Sprint 3 Business Rules

Enrollment/drop enforce common rules:

* Duplicate enrollment is blocked
* Capacity full blocks enrollment
* Prerequisites must be satisfied
* Time conflicts are blocked
* Unit limits:

  * Enrollment cannot exceed max units
  * Dropping cannot violate minimum units
* Current term scoping applies to student schedule/enrollments and professor views

---

## Compatibility Notes (Frontend-Friendly Shims)

To keep frontend integration smooth, the backend supports:

* Unified login: `POST /auth/login`
* Enrollment accepts `course_id` **or** `courseId`
* Legacy endpoints may exist for prerequisites/unit settings and course browsing

These are covered by tests to prevent regressions.

---

## Contributing Workflow

1. Create a branch:

   * `feat/<desc>`, `refactor/<desc>`, `test/<desc>`, `chore/<desc>`
2. Use Conventional Commits:

   * `feat: ...`, `fix: ...`, `refactor: ...`, `test: ...`
3. Open a PR (do not push to `main`)
4. Run tests before PR:

   ```bash
   pytest -q
   ```

---

## Troubleshooting

**`Access denied for user` / MySQL auth errors**

* Confirm username/password in `DATABASE_URL`
* Confirm user privileges and host (`localhost` vs `%`)

**Tables missing**

* Run `python backend/create_db.py`

**JWT errors / unauthorized**

* Confirm `JWT_SECRET_KEY` is set and server restarted after changes

**Swagger not showing endpoints**

* Confirm you’re running `uvicorn backend.app.main:app --reload`
* Confirm routers are included in `backend/app/main.py`

---

If you tell me whether the backend expects `CURRENT_TERM` (it appeared in Sprint 3 tests), I’ll add it explicitly to the `.env.example` section + explain term scoping clearly in the README.
