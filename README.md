# 🎓 StudentAttendance – Hệ thống Điểm danh Sinh viên bằng AI

## Mục lục

- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt nhanh](#cài-đặt-nhanh)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Makefile Commands](#makefile-commands)
- [Quy tắc code](#quy-tắc-code)

---

## Yêu cầu hệ thống

| Tool       | Version | Ghi chú                            |
| ---------- | ------- | ---------------------------------- |
| **Python** | >= 3.11 | Khuyến nghị 3.12                   |
| **Make**   | any     | Windows: dùng `choco install make` |
| **Git**    | >= 2.x  |                                    |

> Database: Supabase PostgreSQL (cloud) – không cần cài Docker.

---

## Cài đặt nhanh

### 1. Clone project

```bash
git clone <repo-url>
cd StudentAttendance
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Cài dependencies

```bash
make install
# hoặc: pip install -r backend/requirements.txt
```

### 4. Cấu hình environment

```bash
cp backend/.env.example backend/.env
# Sửa DATABASE_URL với thông tin Supabase của bạn
```

### 5. Chạy migrations + seed data

```bash
make setup
```

### 6. Chạy server

```bash
make dev
```

Server chạy tại: **http://localhost:8000**
Swagger Docs: **http://localhost:8000/docs**

---

## Cấu trúc dự án

```
StudentAttendance/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── main.py             # Entry point + Exception handlers
│   │   ├── deps.py             # Dependency Injection container
│   │   ├── config/             # Settings, Logging config
│   │   ├── db/                 # Database models, session, base
│   │   ├── dto/                # Request/Response Pydantic models
│   │   ├── repository/         # Data access layer (interfaces + impl)
│   │   ├── services/           # Business logic (interfaces + impl)
│   │   ├── controller/         # Thin orchestration layer
│   │   ├── routes/             # API endpoint declarations
│   │   ├── middleware/         # CORS, Logging, Auth
│   │   └── utils/              # Exceptions, Security, helpers
│   ├── alembic/                # Database migrations
│   ├── .env                    # Environment config (git-ignored)
│   └── requirements.txt
├── ai_core/                    # AI face recognition module (FaceNet512)
├── scripts/                    # Seed data, init scripts
├── Makefile                    # Dev commands
└── README.md
```

### Database Schema (Supabase)

```
roles → users → course_section → class_session → attendance
                                → enrollments
cameras → classrooms
courses → course_section
students → enrollments, attendance
```

---

## Makefile Commands

```bash
make help           # Xem tất cả commands

# ── App ──
make dev            # Chạy dev server (hot reload)
make run            # Chạy production mode

# ── Data ──
make seed           # Seed data mẫu
make setup          # Setup toàn bộ (lần đầu)

# ── Khác ──
make install        # Cài dependencies
make clean          # Xóa __pycache__
```

---

## Quy tắc code

### Layer responsibilities

| Layer          | Nhiệm vụ                                      | KHÔNG được                |
| -------------- | --------------------------------------------- | ------------------------- |
| **Routes**     | Khai báo endpoint, gọi Controller             | Chứa logic                |
| **Controller** | Nhận request → gọi Service → map Response DTO | Chứa business logic       |
| **Service**    | Business logic, throw `BusinessException`     | Import FastAPI, biết HTTP |
| **Repository** | CRUD database                                 | Chứa logic nghiệp vụ      |

---

## Truy cập nhanh

| URL                          | Mô tả        |
| ---------------------------- | ------------ |
| http://localhost:8000        | API Root     |
| http://localhost:8000/docs   | Swagger UI   |
| http://localhost:8000/health | Health check |
