# University Course Registration System

A multi-role course registration platform with **Admin**, **Student**, and **Professor** roles.

* **Admins** manage courses, prerequisites, and unit-limit policies.
* **Students** browse/search courses, **enroll/drop** (current term only), and view a **weekly schedule**.
* **Professors** view their courses, see enrolled students, and (if needed) remove students (current term only).

---

## Table of Contents

* [Project Structure](#project-structure)
* [Tech Stack](#tech-stack)
* [Quick Start (Recommended)](#quick-start-recommended)
* [Backend Setup](#backend-setup)

  * [1) Prerequisites](#1-prerequisites)
  * [2) Environment Variables](#2-environment-variables)
  * [3) Create DB + Tables](#3-create-db--tables)
  * [4) Seed Users (Optional)](#4-seed-users-optional)
  * [5) Run Backend](#5-run-backend)
  * [6) Run Tests](#6-run-tests)
* [Frontend Setup](#frontend-setup)
* [Using the App](#using-the-app)
* [API Overview](#api-overview)
* [Business Rules](#business-rules)
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)

---

## Project Structure

```
course-registration-system/
├─ backend/
│  ├─ app/                  # FastAPI app (routers, services, models)
│  ├─ requirements.txt
│  ├─ create_db.py           # create tables from SQLAlchemy models
│  ├─ seed_initial_admin.py
│  ├─ seed_initial_student.py
│  └─ seed_initial_professor.py
└─ frontend/
   ├─ panel/                 # Admin panel (RTL Persian UI)
   ├─ student-panel/         # Student panel
   ├─ professor-panel/       # Professor panel
   └─ JS/config.js           # API base URL config
```

---

## Tech Stack

**Backend**

* Python 3.10+
* FastAPI
* SQLAlchemy ORM
* MySQL
* JWT authentication

**Frontend**

* Static HTML/CSS + Vanilla JS modules (RTL / Persian)

**Testing**

* pytest (+ FastAPI TestClient)

---

## Quick Start (Recommended)

### 1) Start backend

```bash
cd course-registration-system
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r backend/requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

python backend/create_db.py
uvicorn backend.app.main:app --reload
```

Backend:

* API: `http://127.0.0.1:8000`
* Swagger docs: `http://127.0.0.1:8000/docs`

### 2) Start frontend

```bash
cd frontend
python -m http.server 8001
```

Open in browser:

* Login panel: `http://127.0.0.1:8001/Login/index.html`

> The frontend expects backend at `http://127.0.0.1:8000` by default.
> If your backend runs elsewhere, update `frontend/JS/config.js`.

---

## Backend Setup

### 1) Prerequisites

* Python **3.10+**
* MySQL server running locally (or accessible remotely)
* A MySQL database created (example below)

### 2) Environment Variables

Copy `.env.example` → `.env`:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and set at least:

* `DATABASE_URL` (SQLAlchemy URL)
* `JWT_SECRET_KEY` (strong secret)
* `CURRENT_TERM` (example: `1404-2`)

Example `DATABASE_URL`:

```env
DATABASE_URL=mysql+pymysql://crs_user:strong_password@localhost:3306/course_registration_db
```

### 3) Create DB + Tables

Create DB and user (example):

```sql
CREATE DATABASE course_registration_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'crs_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON course_registration_db.* TO 'crs_user'@'localhost';
FLUSH PRIVILEGES;
```

Then create tables:

```bash
python backend/create_db.py
```

### 4) Seed Users (Optional)

These scripts help you quickly test the UI.

```bash
python backend/seed_initial_admin.py
python backend/seed_initial_student.py
python backend/seed_initial_professor.py
```

use their password and username for logging 
They read credentials from environment variables. Check `.env.example` for names like:

* `INITIAL_ADMIN_*`
* `SEED_STUDENT_*`
* `INITIAL_PROFESSOR_*`

⚠️ **Do not use default/dev credentials in production.**

### 5) Run Backend

From repo root:

```bash
uvicorn backend.app.main:app --reload
```

* API base: `http://127.0.0.1:8000`
* Swagger: `http://127.0.0.1:8000/docs`

### 6) Run Tests

From repo root:

```bash
pytest -q
```

---

## Frontend Setup

This project uses a static frontend; it must be served via an HTTP server (opening `file://` directly may break API calls).

### Option A) Python HTTP server (simple)

```bash
cd frontend
python -m http.server 8001
```

### Option B) VS Code Live Server

1. Install the **Live Server** extension
2. Open `frontend/` in VS Code
3. Right-click `panel/index.html` → “Open with Live Server”

---

## Using the App

1. **Start backend** (`uvicorn ...`)
2. **Start frontend** (`python -m http.server 8001`)
3. Login from any panel using seeded credentials (or your own DB users)

---

## API Overview

Auth is JWT-based. Protected endpoints require:

```
Authorization: Bearer <token>
```

### Auth

* `POST /auth/login`
  A unified login endpoint (tries admin/student/professor).

### Admin

* `GET/POST /api/courses`
* `GET/PUT/DELETE /api/courses/{id}`
* `GET/POST /api/courses/{id}/prerequisites`
* `DELETE /api/courses/{id}/prerequisites/{prereq_id}`
* `GET/PUT /api/admin/unit-limits`

### Student

* `GET /api/student/courses` (catalogue)
* `POST /api/student/enrollments` (enroll; accepts `course_id` or `courseId`)
* `GET /api/student/enrollments` (current-term enrollments)
* `DELETE /api/student/enrollments/{course_id}` (drop; current term only)
* `GET /api/student/schedule` (weekly schedule)

### Professor

* `GET /api/professor/courses` (current term)
* `GET /api/professor/courses/{id}/students`
* `DELETE /api/professor/courses/{id}/students/{student_id}` (remove; current term only)

---

## Business Rules

Enrollment/drop/removal enforce key constraints:

* No duplicate enrollments
* Capacity must allow enrollment
* Prerequisites must be satisfied
* No time conflicts
* Unit limits:

  * cannot exceed max units
  * dropping cannot go below min units
* Student/professor operations are scoped to **CURRENT_TERM**

---

## Troubleshooting

### MySQL auth/connection errors

* Verify `DATABASE_URL`
* Ensure MySQL is running
* Ensure the user has privileges on the DB

### Missing tables

Run:

```bash
python backend/create_db.py
```

### JWT “Unauthorized”

* Ensure `JWT_SECRET_KEY` is set
* Restart the backend after changing `.env`

### Frontend doesn’t call backend / CORS issues

* Make sure frontend is served over HTTP (not `file://`)
* Confirm the API base URL in `frontend/JS/config.js`

### Swagger shows no endpoints

* Ensure routers are included in `backend.app.main`
* Ensure you’re running:

```bash
uvicorn backend.app.main:app --reload
```

---

## Contributing

* Create a branch: `feat/...`, `refactor/...`, `test/...`
* Use clear commit messages (Conventional Commits recommended)
* Run tests before PR:

```bash
pytest -q
```
