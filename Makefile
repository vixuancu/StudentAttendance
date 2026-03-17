# ============================================================
# StudentAttendance – Makefile
# Chạy: make <command>
# ============================================================

# ── App ──────────────────────────────────────────────────────
dev:  ## Chạy backend dev server (hot reload)
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run:  ## Chạy backend production mode
	cd backend && uvicorn src.main:app --host 0.0.0.0 --port 8000

# ── Seed Data ────────────────────────────────────────────────
seed:  ## Chạy seed data mẫu
	cd backend && python ../scripts/seed_data.py

# ── Dependencies ─────────────────────────────────────────────
install:  ## Cài đặt dependencies
	pip install -r backend/requirements.txt

# ── Setup nhanh cho dev mới ──────────────────────────────────
setup:  ## Setup toàn bộ: install + seed (chạy lần đầu)
	@echo "🚀 Setting up StudentAttendance..."
	make install
	make seed
	@echo "✅ Setup xong! Chạy: make dev"

# ── Clean ────────────────────────────────────────────────────
clean:  ## Xóa __pycache__, .pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	echo "✅ Cleaned"

# ── Help ─────────────────────────────────────────────────────
help:  ## Hiện danh sách commands
	@echo Available commands:
	@echo   make dev      - Chay backend dev server (hot reload)
	@echo   make run      - Chay backend production mode
	@echo   make seed     - Chay seed data mau
	@echo   make install  - Cai dat dependencies
	@echo   make setup    - Setup toan bo: install + seed
	@echo   make clean    - Xoa __pycache__, .pyc
	@echo   make help     - Hien danh sach commands

.PHONY: dev run seed install setup clean help
.DEFAULT_GOAL := help
