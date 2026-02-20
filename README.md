# 🎓 StudentAttendance – Hệ thống Điểm danh Sinh viên bằng AI

## Mục lục

- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt nhanh (5 phút)](#cài-đặt-nhanh-5-phút)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Makefile Commands](#makefile-commands)
- [Quy tắc code](#quy-tắc-code)
- [Git Workflow](#git-workflow)

---

## Yêu cầu hệ thống

| Tool       | Version | Ghi chú                            |
| ---------- | ------- | ---------------------------------- |
| **Python** | >= 3.11 | Khuyến nghị 3.12                   |
| **Docker** | >= 24.x | Chạy PostgreSQL                    |
| **Make**   | any     | Windows: dùng `choco install make` |
| **Git**    | >= 2.x  |                                    |

---
Typography
## Cài đặt nhanh (5 phút)

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
# Copy file env mẫu
cp backend/.env.example backend/.env

# Sửa nếu cần (mặc định đã OK cho dev local)
```

### 5. Setup một lệnh (DB + migrate + seed)

```bash
make setup
```

> Lệnh này sẽ: khởi động PostgreSQL Docker → chạy migrations → seed data mẫu

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
├── ai_core/                    # AI face recognition module
├── scripts/                    # Seed data, init scripts
├── docker-compose.yml          # PostgreSQL + pgAdmin
├── Makefile                    # Dev commands
└── README.md
```

### Kiến trúc layered

```
Route (thin) → Controller (map DTO) → Service (business logic) → Repository (DB)
```

> Chi tiết kiến trúc: xem file `.agent/workflows/project-structure.md`

---

## Makefile Commands

```bash
make help           # Xem tất cả commands

# ── App ──
make dev            # Chạy dev server (hot reload)
make run            # Chạy production mode

# ── Database ──
make db-up          # Khởi động PostgreSQL Docker
make db-down        # Tắt Docker
make db-reset       # Xóa DB + khởi động lại

# ── Migrations ──
make migrate                        # Chạy migrations
make migrate-create m="add_xyz"     # Tạo migration mới
make migrate-down                   # Rollback 1 migration
make migrate-history                # Xem lịch sử

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

### Tạo API mới (checklist)

1. `src/repository/interfaces/i_xxx_repo.py`
2. `src/repository/xxx_repo.py`
3. `src/services/interfaces/i_xxx_service.py`
4. `src/services/xxx_service.py`
5. `src/controller/xxx_controller.py`
6. `src/deps.py` — đăng ký DI
7. `src/routes/v1/xxx_routes.py`
8. `src/routes/router.py` — include router

### Import rules

```python
# ✅ ĐÚNG
from src.config.settings import settings
from src.db.models.student import Student

# ❌ SAI
from backend.src.config.settings import settings
```

---

## Git Workflow

### Branch naming

```
feature/SA-xxx-mô-tả     # Tính năng mới
bugfix/SA-xxx-mô-tả      # Sửa bug
hotfix/SA-xxx-mô-tả      # Fix khẩn cấp
```

### Commit message format

```
feat: thêm API tạo sinh viên
fix: sửa lỗi pagination student
refactor: tách service logic
docs: cập nhật README
```

### Flow

1. Tạo branch từ `develop`
2. Code + test
3. Push + tạo Pull Request
4. Review → Merge vào `develop`

---

## Truy cập nhanh

| URL                          | Mô tả            |
| ---------------------------- | ---------------- |
| http://localhost:8000        | API Root         |
| http://localhost:8000/docs   | Swagger UI       |
| http://localhost:8000/health | Health check     |
| http://localhost:5050        | pgAdmin (DB GUI) |

**pgAdmin login**: `admin@admin.com` / `admin`
