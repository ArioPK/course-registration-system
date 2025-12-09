# 🎓 Course Registration System

> A comprehensive, full-stack university course registration platform featuring a **FastAPI** backend and a **Vanilla JavaScript (MVC)** frontend.

![Project Status](https://img.shields.io/badge/Status-Sprint%201%20Complete-success)
![Python](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)
![JavaScript](https://img.shields.io/badge/Frontend-Vanilla%20JS%20(MVC)-yellow?logo=javascript)
![Database](https://img.shields.io/badge/Database-MySQL-4479A1?logo=mysql&logoColor=white)

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)

---

## 📖 Overview

The **Course Registration System** is designed to streamline the academic administration process. In its current phase (Sprint 1), it provides a secure **Admin Panel** that allows university administrators to manage course listings, capacities, and scheduling through a responsive and intuitive user interface.

The system emphasizes clean code architecture, utilizing a classic **MVC (Model-View-Controller)** pattern on both the backend and the frontend to ensure scalability and maintainability.

---

## ✨ Key Features

### 🔐 Authentication & Security
- **Secure Admin Login:** JWT (JSON Web Token) based authentication.
- **Password Hashing:** Industry-standard Argon2id hashing for password storage.
- **Session Management:** Secure handling of user sessions and auto-redirects via `AuthService`.

### 📚 Course Management (CRUD)
- **Create:** Add new courses with detailed attributes (Code, Name, Professor, Schedule, Capacity, etc.).
- **Read:** View paginated lists of courses with dynamic filtering by Department or Semester.
- **Update:** Edit existing course details instantly.
- **Delete:** Remove courses with safety confirmation modals.

### 🎨 User Interface & Experience
- **Responsive Design:** Fully optimized for Desktop, Tablet, and Mobile devices.
- **Real-time Validation:** Instant feedback on forms using `CourseValidator` and `LoginValidator`.
- **Dashboard Statistics:** At-a-glance summary of total courses, capacity, and enrollment.

---

## 🏗 Architecture

### Backend (FastAPI)
Follows a layered architecture:
1.  **Routers:** Handle HTTP requests (`backend/app/routers`).
2.  **Services:** Business logic and validation (`backend/app/services`).
3.  **Repositories:** Direct database interactions (`backend/app/repositories`).
4.  **Models/Schemas:** SQLAlchemy ORM models and Pydantic schemas.

### Frontend (Vanilla JS)
Implements a strict **MVC Pattern** without external frameworks:
1.  **Model:** API communication (`api.service.js`) and Auth logic.
2.  **View:** DOM manipulation and rendering (`renderer.js`, `login.view.js`).
3.  **Controller:** Connects Model and View (`course.controller.js`).

---

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.10+
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Security:** Python-Jose (JWT), Argon2-cffi
- **Testing:** Pytest

### Frontend
- **Core:** HTML5, CSS3, JavaScript (ES6 Modules)
- **Styling:** CSS Variables, Flexbox, Grid.
- **Icons:** Remix Icons

---

## 📂 Project Structure

```graphql
course-registration-system/
├── backend/
│   ├── app/
│   │   ├── config/          # Configuration settings
│   │   ├── models/          # Database Models
│   │   ├── routers/         # API Routes
│   │   ├── services/        # Business Logic
│   │   └── main.py          # App Entry Point
│   ├── create_db.py         # DB Init Script
│   ├── seed_initial_admin.py# Admin Seeder Script
│   └── requirements.txt     # Dependencies
│
├── frontend/
│   ├── CSS/                 # Global Styles
│   ├── JS/
│   │   ├── controllers/     # MVC Controllers
│   │   ├── services/        # API & Auth Services
│   │   └── ui/              # View Logic
│   ├── Login/               # Login Page
│   └── panel/               # Admin Panel
│
└── docs/                    # Documentation
