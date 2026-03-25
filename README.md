# StudentAttendance Backend Guide

Backend API cho hệ thống diem danh sinh vien bang AI, duoc xay dung voi FastAPI + SQLAlchemy Async.

README nay tap trung vao 2 muc tieu:
- Giup nguoi moi chay duoc project nhanh.
- Giup dev moi hieu luong code de tiep tuc phat trien ma khong bi roi.

## 1) Tong quan nhanh

- Kieu kien truc: Route -> Controller -> Service -> Repository -> Database.
- Prefix API: `/api/v1`.
- Auth: JWT Bearer token.
- Database: PostgreSQL (uu tien Supabase), ket noi async qua `asyncpg`.
- Response format thong nhat: `success`, `message`, `data` (hoac `details` khi loi).

## 2) Chay project trong 5 phut

### Yeu cau

- Python >= 3.11
- Git
- Make (khuyen nghi)

### Cai dat

```bash
git clone <repo-url>
cd StudentAttendance

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

make install
```

### Cau hinh env

```bash
# Windows PowerShell
Copy-Item backend/.env.example backend/.env

# macOS/Linux
cp backend/.env.example backend/.env
```

Bat buoc sua it nhat:
- `DATABASE_URL`
- `SECRET_KEY`

Tuy chon toi uu response:
- `GZIP_ENABLED=true`
- `GZIP_MINIMUM_SIZE=1024`
- `GZIP_COMPRESSLEVEL=5`

### Chay server

```bash
make dev
```

Kiem tra:
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## 3) Cau truc thu muc va y nghia

```text
StudentAttendance/
|- backend/
|  |- src/
|  |  |- main.py                 # Tao app, middleware, exception handlers
|  |  |- routes/                 # Khai bao endpoint (HTTP layer)
|  |  |- controller/             # Dieu phoi request/response DTO
|  |  |- services/               # Business logic
|  |  |- repository/             # Truy van DB
|  |  |- dto/                    # Request/Response schemas
|  |  |- db/                     # SQLAlchemy models, session, base
|  |  |- middleware/             # Auth dependency, CORS, logging
|  |  |- utils/                  # Security, exceptions, helpers
|  |  |- config/                 # Settings, logging config
|  |- .env.example
|  |- requirements.txt
|- ai_core/
|- scripts/
|- Makefile
```

## 4) Luong code backend (de hieu nhanh)

Vi du voi login:

1. Route nhan request HTTP trong `backend/src/routes/v1/auth_routes.py`.
2. Route goi Controller (`AuthController`).
3. Controller goi Service (`AuthService`) de xu ly business.
4. Service goi Repository (`UserRepository`) de lay user tu DB.
5. Service tao JWT, tra lai Controller.
6. Controller map ve DTO va tra response thong nhat cho client.

Ly do tach layer nhu vay:
- De test va thay doi de dang.
- Service khong phu thuoc FastAPI (de tai su dung).
- Route gon, doc de.

## 5) Auth + JWT dang duoc su dung

### Endpoint auth hien co

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

### Login request

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Login response (rut gon)

```json
{
  "success": true,
  "message": "Dang nhap thanh cong",
  "data": {
    "token": {
      "access_token": "<jwt>",
      "token_type": "bearer"
    },
    "user": {
      "id": 1,
      "username": "admin",
      "full_name": "Nguyen Van A",
      "email": "admin@edu.vn",
      "role_id": 1,
      "role_name": "admin"
    }
  }
}
```

### JWT duoc dung the nao

- Payload co `sub` (user id), `username`, `role_id`, `exp`.
- API can auth doc token tu header `Authorization: Bearer <token>`.
- Dependency `get_current_user` giai ma token, load user DB, chan user bi vo hieu hoa.
- Dependency `require_roles(...)` dung de chan theo role ngay tai route.

## 6) Phan quyen hien tai

- FE co the an/hien menu theo role, nhung BE moi la noi chan that.
- Vi du `students` da duoc chan bang role `admin`, `giao_vu`.
- Neu mo rong route moi, uu tien them `Depends(require_roles(...))` tai route.

## 7) Error format thong nhat

Tat ca loi deu duoc handler trong `backend/src/main.py`.

Mau co ban:

```json
{
  "success": false,
  "message": "Noi dung loi",
  "error_code": "UNAUTHORIZED"
}
```

Validation loi co them `details`.

## 8) Makefile commands hay dung

```bash
make help      # xem toan bo lenh
make install   # cai dependencies
make dev       # chay dev server
make run       # chay mode thuong
make setup     # install + seed (neu co script seed)
make clean     # xoa __pycache__ va .pyc
```

## 9) Danh gia nhanh base hien tai (uu/nhuoc)

### Diem on

- Kien truc layer ro rang, de onboard.
- Exception handling tong hop tai mot cho.
- Auth flow da day du login/me/change-password.
- Co middleware auth va role guard o BE.

### Diem can nang cap tiep

- Chua co migration tool (nen bo sung Alembic som).
- Mot so route v1 dang rong (`attendance_routes.py`, `class_routes.py`, `recognition_routes.py`).
- DB session dang auto-commit theo request; can giu ky luat transaction khi nghiep vu phuc tap hon.
- Nen bo sung test auth/permission o muc API.

## 10) Quy tac phat trien de code ben

- Route chi lam viec HTTP + dependency injection.
- Controller chi map request/response, khong viet business logic.
- Service chua business logic va throw `BusinessException`.
- Repository chi lo DB query.
- Moi endpoint moi can:
  - DTO request/response ro rang
  - auth/phong quyen neu can
  - thong diep loi nhat quan

## 11) Checklist debug thuong gap

- 401 ngay ca khi da login:
  - Kiem tra header `Authorization` co dung `Bearer`.
  - Kiem tra `SECRET_KEY` giua moi truong co bi lech.
- FE goi khong dung route:
  - Nho prefix dung la `/api/v1`.
- Loi CORS:
  - Them origin FE vao `CORS_ORIGINS` trong `backend/.env`.
- Login fail du credentials dung:
  - Kiem tra password trong DB da duoc hash bcrypt.

## 12) Huong mo rong tiep theo

- Them Alembic migration.
- Them bo test cho auth + role permission.
- Hoan thien route attendance/class/recognition.
- Sau khi schema DB chot, moi them chuc nang tao tai khoan.

---

Neu ban moi vao team, hay doc theo thu tu nay de nam he thong nhanh:

1. `backend/src/main.py`
2. `backend/src/routes/router.py`
3. `backend/src/routes/v1/auth_routes.py`
4. `backend/src/controller/auth_controller.py`
5. `backend/src/services/auth_service.py`
6. `backend/src/middleware/auth.py`
7. `backend/src/db/session.py`

Doc xong 7 file tren la da hieu hon 80% luong backend hien tai.
