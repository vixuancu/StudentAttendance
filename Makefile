# ============================================================
# StudentAttendance – Makefile
# Chạy: make <command>
# ============================================================

ifeq ($(OS),Windows_NT)
PYTHON := python
SEED_CMD := powershell -NoProfile -Command "if (Test-Path 'scripts/seed_data.py') { & python scripts/seed_data.py } else { Write-Host '⚠️  Không tìm thấy scripts/seed_data.py, bỏ qua seed.' }"
CLEAN_CMD := powershell -NoProfile -Command "Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue; Get-ChildItem -Path . -Recurse -File -Include *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue; Write-Host '✅ Cleaned'"
else
PYTHON := python3
SEED_CMD := if [ -f scripts/seed_data.py ]; then $(PYTHON) scripts/seed_data.py; else echo "⚠️  Không tìm thấy scripts/seed_data.py, bỏ qua seed."; fi
CLEAN_CMD := find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	echo "✅ Cleaned"
endif

# ── App ──────────────────────────────────────────────────────
dev:  ## Chạy backend dev server (hot reload)
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run:  ## Chạy backend production mode
	cd backend && uvicorn src.main:app --host 0.0.0.0 --port 8000

# ── Seed Data ────────────────────────────────────────────────
seed:  ## Chạy seed data mẫu
	@$(SEED_CMD)

# ── Dependencies ─────────────────────────────────────────────
install:  ## Cài đặt dependencies
	$(PYTHON) -m pip install -r backend/requirements.txt

# ── Setup nhanh cho dev mới ──────────────────────────────────
setup:  ## Setup toàn bộ: install + seed (chạy lần đầu)
	@echo "🚀 Setting up StudentAttendance..."
	@$(MAKE) install
	@$(MAKE) seed
	@echo "✅ Setup xong! Chạy: make dev"

# ── Clean ────────────────────────────────────────────────────
clean:  ## Xóa __pycache__, .pyc
	@$(CLEAN_CMD)

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
