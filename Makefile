# ============================================================
# StudentAttendance – Makefile
# Chạy: make <command>
# ============================================================

# ── App ──────────────────────────────────────────────────────
dev:  ## Chạy backend dev server (hot reload)
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run:  ## Chạy backend production mode
	cd backend && uvicorn src.main:app --host 0.0.0.0 --port 8000

# ── Database ─────────────────────────────────────────────────
db-up:  ## Khởi động PostgreSQL + pgAdmin bằng Docker
	docker compose up -d

db-down:  ## Tắt Docker containers
	docker compose down

db-reset:  ## Xóa toàn bộ DB data và khởi động lại
	docker compose down -v
	docker compose up -d

db-logs:  ## Xem logs PostgreSQL
	docker compose logs -f db

# ── Migrations ───────────────────────────────────────────────
migrate:  ## Chạy tất cả migrations (upgrade to head)
	cd backend && alembic upgrade head

migrate-create:  ## Tạo migration mới: make migrate-create m="tên migration"
	cd backend && alembic revision --autogenerate -m "$(m)"

migrate-down:  ## Rollback 1 migration
	cd backend && alembic downgrade -1

migrate-history:  ## Xem lịch sử migrations
	cd backend && alembic history --verbose

migrate-current:  ## Xem migration hiện tại
	cd backend && alembic current

# ── Seed Data ────────────────────────────────────────────────
seed:  ## Chạy seed data mẫu
	cd backend && python ../scripts/seed_data.py

# ── Dependencies ─────────────────────────────────────────────
install:  ## Cài đặt dependencies
	pip install -r backend/requirements.txt

# ── Setup nhanh cho dev mới ──────────────────────────────────
setup:  ## Setup toàn bộ: DB + migrate + seed (chạy lần đầu)
	@echo "🚀 Setting up StudentAttendance..."
	make db-up
	@echo "⏳ Chờ DB khởi động..."
	timeout /t 5 /nobreak >nul 2>&1 || sleep 5
	make migrate
	make seed
	@echo "✅ Setup xong! Chạy: make dev"

# ── Clean ────────────────────────────────────────────────────
clean:  ## Xóa __pycache__, .pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	echo "✅ Cleaned"

# ── Help ─────────────────────────────────────────────────────
help:  ## Hiện danh sách commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: dev run db-up db-down db-reset db-logs migrate migrate-create migrate-down migrate-history migrate-current seed install setup clean help
.DEFAULT_GOAL := help
