# run dev
dev:
	cd backend && uvicorn src.main:app --reload

# run migrations
migrate:
	cd backend && alembic upgrade head

# create migrations (chưa test từ từ, xem sau)
mk-migrate:
	cd backend && alembic revision --autogenerate -m "$*"

# rollback migrations
rollback:
	cd backend && alembic downgrade -1
	


