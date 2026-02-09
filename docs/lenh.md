
Từ giờ khi bạn gõ /project-structure, tôi sẽ đọc file này và tuân theo kiến trúc dự án của bạn.


# khi cần update DB thì sửa vào model xem tương tự rồi update chạy migration
các câu lệnh thao tác 
pip install -r requirements.txt 


Base database khóa luận
# 1. Vào thư mục backend
cd c:\D\KHOALUAN\DoAn\backend\StudentAttendance\backend

# 2. Cài dependencies
pip install -r requirements.txt

# 3. Copy .env.example thành .env và sửa thông tin DB
copy .env.example .env

# 4. Tạo database trong PostgreSQL (dùng psql hoặc pgAdmin)
# CREATE DATABASE student_attendance;

# 5. Tạo migration đầu tiên
alembic revision --autogenerate -m "Initial migration"

# 6. Chạy migration
alembic upgrade head

# 7. Chạy server
uvicorn src.main:app --reload