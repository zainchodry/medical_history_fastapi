# 🏥 Medical History API

A **production-grade REST API** for managing medical history, patients, appointments, prescriptions, and audit logs — built with **FastAPI**, **SQLAlchemy**, and **Pydantic V2**.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [API Endpoints](#-api-endpoints)
- [Authentication](#-authentication)
- [Role-Based Access Control](#-role-based-access-control)
- [Audit Logging](#-audit-logging)
- [License](#-license)

---

## ✨ Features

- **JWT Authentication** — Secure token-based auth with login, register, and password reset flows
- **Role-Based Access Control** — Three roles: `doctor`, `patient`, `admin` with granular permissions
- **Full CRUD Operations** — Create, Read, Update, Delete for all resources
- **Pagination & Filtering** — `skip`/`limit` query params on all list endpoints with search/filter support
- **Patient Management** — Enhanced profiles with blood type, allergies, and emergency contacts
- **Appointment Scheduling** — Time-slot conflict detection, status management (scheduled → completed/cancelled/no-show)
- **Prescription System** — Multi-medicine prescriptions with dosage, frequency, and duration tracking
- **Medical Records** — Doctor-authored clinical records with diagnosis, treatment, and visit dates
- **Dashboard & Statistics** — Aggregate counts, today's schedule, and recent patient activity
- **Audit Trail** — Automatic logging of all create/update/delete operations with filterable API
- **Password Reset** — Email-based forgot/reset password flow via SMTP
- **CORS Middleware** — Pre-configured for cross-origin requests
- **Global Error Handling** — Structured JSON error responses

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.135+ |
| **ORM** | SQLAlchemy 2.0 |
| **Validation** | Pydantic V2 + pydantic-settings |
| **Auth** | python-jose (JWT) + passlib + bcrypt |
| **Email** | fastapi-mail (async SMTP) |
| **Token Utils** | itsdangerous (password reset tokens) |
| **Database** | SQLite (default, swappable to PostgreSQL/MySQL) |
| **Python** | 3.11+ |

---

## 📁 Project Structure

```
medical_history_fastapi/
├── .env                    # Environment variables (git-ignored)
├── .env.example            # Template for environment variables
├── .gitignore              # Git ignore rules
├── requirements.txt        # Pinned Python dependencies
├── README.md               # This file
│
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI app, CORS, lifespan, routers
    ├── config.py           # Pydantic Settings (reads from .env)
    ├── database.py         # SQLAlchemy engine, session, Base
    │
    ├── models/             # SQLAlchemy ORM models
    │   ├── __init__.py
    │   ├── user.py         # User + UserRole enum
    │   ├── patient.py      # Patient (enhanced profile)
    │   ├── appointment.py  # Appointment + AppointmentStatus enum
    │   ├── medical_record.py
    │   ├── prescription.py # Prescription + Medicine
    │   └── audit_log.py    # AuditLog
    │
    ├── schemas/            # Pydantic V2 request/response schemas
    │   ├── __init__.py
    │   ├── user.py         # UserCreate, UserLogin, UserOut, TokenSchema, etc.
    │   ├── patient.py      # PatientCreate, PatientUpdate, PatientOut
    │   ├── appointment.py  # AppointmentCreate, AppointmentUpdate, AppointmentOut
    │   ├── medical_record.py
    │   ├── prescription.py # PrescriptionCreate, MedicineSchema, PrescriptionOut
    │   └── audit_log.py    # AuditLogOut
    │
    ├── routes/             # API route handlers
    │   ├── __init__.py
    │   ├── auth.py         # Register, Login, Profile, Password flows
    │   ├── patient.py      # CRUD + search/filter
    │   ├── appointment.py  # CRUD + status management
    │   ├── medical_record.py
    │   ├── prescription.py # CRUD with nested medicines
    │   ├── dashboard.py    # Statistics & overview
    │   └── audit_log.py    # Filterable audit trail
    │
    └── utils/              # Shared utilities
        ├── __init__.py
        ├── auth.py         # create_access_token (JWT)
        ├── deps.py         # get_current_user dependency, CurrentUserDep
        ├── permissions.py  # role_required dependency factory
        ├── password.py     # hash_password, verify_password (bcrypt)
        ├── token.py        # Password reset token (itsdangerous)
        └── email.py        # Async email sender (fastapi-mail)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/medical_history_fastapi.git
cd medical_history_fastapi

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your actual values (see Environment Variables below)

# 5. Run the development server
fastapi dev app/main.py
```

The API will be available at **http://127.0.0.1:8000**

- **Swagger UI** → http://127.0.0.1:8000/docs
- **ReDoc** → http://127.0.0.1:8000/redoc

> **Note:** Database tables are automatically created on first startup via the `lifespan` context manager. No manual migration step is required for SQLite.

---

## 🔐 Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

| Variable | Description | Default |
|----------|-------------|---------|
| `SQLALCHEMY_DATABASE_URL` | Database connection string | `sqlite:///./medical_history.db` |
| `SECRET_KEY` | JWT signing key (**change in production!**) | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry in minutes | `60` |
| `MAIL_USERNAME` | SMTP email address | — |
| `MAIL_PASSWORD` | SMTP app password | — |
| `MAIL_FROM` | Sender email address | — |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `FRONTEND_URL` | Frontend URL for password reset links | `http://localhost:3000` |

---

## 📖 API Documentation

Interactive documentation is auto-generated by FastAPI:

| URL | Interface |
|-----|-----------|
| `/docs` | **Swagger UI** — Interactive API explorer with "Try it out" |
| `/redoc` | **ReDoc** — Clean, readable API reference |

---

## 🔗 API Endpoints

### Root & Health

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | API metadata (name, version, docs links) | ❌ |
| `GET` | `/health` | Health check | ❌ |

### Authentication (`/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/auth/register` | Register a new user | ❌ |
| `POST` | `/auth/login` | Login and receive JWT | ❌ |
| `GET` | `/auth/me` | Get current user profile | ✅ |
| `PUT` | `/auth/me` | Update current user profile | ✅ |
| `POST` | `/auth/change-password` | Change password (authenticated) | ✅ |
| `POST` | `/auth/forgot-password` | Request password reset email | ❌ |
| `POST` | `/auth/reset-password/{token}` | Reset password using token | ❌ |
| `GET` | `/auth/users` | List all users (admin only) | ✅ 🔒 |

### Patients (`/patients`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/patients/` | Create a patient | ✅ 🔒 Doctor/Admin |
| `GET` | `/patients/` | List patients (search, filter, paginate) | ✅ 🔒 Doctor/Admin |
| `GET` | `/patients/{id}` | Get patient by ID | ✅ 🔒 Doctor/Admin |
| `PUT` | `/patients/{id}` | Update patient | ✅ 🔒 Doctor/Admin |
| `DELETE` | `/patients/{id}` | Delete patient | ✅ 🔒 Doctor/Admin |

**Query Parameters:** `skip`, `limit`, `search` (by name), `gender`, `blood_type`

### Appointments (`/appointments`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/appointments/` | Create appointment (with conflict detection) | ✅ |
| `GET` | `/appointments/` | List appointments (filter by status) | ✅ |
| `GET` | `/appointments/{id}` | Get appointment by ID | ✅ |
| `PUT` | `/appointments/{id}` | Update appointment | ✅ 🔒 Doctor/Admin |
| `PATCH` | `/appointments/{id}/status` | Change status (cancel/complete/no-show) | ✅ |
| `DELETE` | `/appointments/{id}` | Delete appointment | ✅ 🔒 Doctor/Admin |

**Query Parameters:** `skip`, `limit`, `status`

### Medical Records (`/records`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/records/` | Create medical record | ✅ 🔒 Doctor |
| `GET` | `/records/` | List records (filter, search, paginate) | ✅ 🔒 Doctor/Admin |
| `GET` | `/records/{id}` | Get record by ID | ✅ 🔒 Doctor/Admin |
| `PUT` | `/records/{id}` | Update record | ✅ 🔒 Doctor |
| `DELETE` | `/records/{id}` | Delete record | ✅ 🔒 Doctor |

**Query Parameters:** `skip`, `limit`, `patient_id`, `search` (by title/diagnosis)

### Prescriptions (`/prescriptions`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/prescriptions/` | Create prescription with medicines | ✅ 🔒 Doctor |
| `GET` | `/prescriptions/` | List prescriptions (paginate, filter) | ✅ 🔒 Doctor/Admin |
| `GET` | `/prescriptions/{id}` | Get prescription by ID | ✅ 🔒 Doctor/Admin |
| `PUT` | `/prescriptions/{id}` | Update prescription notes | ✅ 🔒 Doctor |
| `DELETE` | `/prescriptions/{id}` | Delete prescription (cascades medicines) | ✅ 🔒 Doctor |

**Query Parameters:** `skip`, `limit`, `patient_id`

### Dashboard (`/dashboard`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/dashboard/stats` | Aggregated statistics & today's schedule | ✅ 🔒 Doctor/Admin |

**Returns:** `total_patients`, `total_appointments`, `today_appointments`, `upcoming_appointments`, `total_medical_records`, `total_prescriptions`, `recent_patients`, `todays_schedule`

### Audit Logs (`/audit-logs`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/audit-logs/` | Filterable audit trail | ✅ 🔒 Doctor/Admin |

**Query Parameters:** `skip`, `limit`, `action` (CREATE/UPDATE/DELETE), `resource` (patient/appointment/etc.)

---

## 🔑 Authentication

This API uses **JWT Bearer Token** authentication.

### Register & Login Flow

```bash
# 1. Register a new user
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "username": "Dr. Smith",
    "password": "securepass123",
    "role": "doctor"
  }'

# 2. Login to get a token
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "securepass123"
  }'
# Response: { "access_token": "eyJ...", "token_type": "bearer" }

# 3. Use the token in subsequent requests
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer eyJ..."
```

---

## 🛡 Role-Based Access Control

| Role | Permissions |
|------|-------------|
| **`doctor`** | Full CRUD on patients, records, prescriptions, appointments. Access to dashboard and audit logs. |
| **`admin`** | Same as doctor + user management |
| **`patient`** | View own appointments, cancel own appointments |

---

## 📝 Audit Logging

Every **create**, **update**, and **delete** operation is automatically logged to the `audit_logs` table with:

- `user_id` — Who performed the action
- `action` — `CREATE`, `UPDATE`, `DELETE`, `STATUS_CHANGE`
- `resource` — `patient`, `appointment`, `medical_record`, `prescription`, `user`
- `resource_id` — ID of the affected resource
- `details` — Additional context (e.g., status changes)
- `created_at` — Timestamp

---

## 📄 License

This project is for educational and portfolio purposes.
