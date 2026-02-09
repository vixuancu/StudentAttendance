"""
Seed data mẫu cho development.
Chạy: make seed  (hoặc: cd backend && python -m scripts.seed_data)
"""

import asyncio
import sys
from pathlib import Path

# Thêm backend/ vào sys.path để import src.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from src.db.session import async_session_factory, engine
from src.db.models.student import Student
from src.db.models.user import User, Lecturer
from src.db.models.enums import StudentStatus, UserRole


# ── Sample Data ──────────────────────────────────────────────

STUDENTS = [
    {
        "student_code": "2020CNTT001",
        "full_name": "Nguyễn Văn An",
        "class_code": "CNTT01",
        "email": "nguyenvanan@hou.edu.vn",
        "phone": "0901234001",
        "enrollment_year": 2020,
        "status": StudentStatus.ACTIVE,
    },
    {
        "student_code": "2020CNTT002",
        "full_name": "Trần Thị Bình",
        "class_code": "CNTT01",
        "email": "tranthibinh@hou.edu.vn",
        "phone": "0901234002",
        "enrollment_year": 2020,
        "status": StudentStatus.ACTIVE,
    },
    {
        "student_code": "2020CNTT003",
        "full_name": "Lê Hoàng Cường",
        "class_code": "CNTT02",
        "email": "lehoangcuong@hou.edu.vn",
        "phone": "0901234003",
        "enrollment_year": 2020,
        "status": StudentStatus.ACTIVE,
    },
    {
        "student_code": "2021CNTT004",
        "full_name": "Phạm Minh Đức",
        "class_code": "CNTT02",
        "email": "phamminhduc@hou.edu.vn",
        "phone": "0901234004",
        "enrollment_year": 2021,
        "status": StudentStatus.ACTIVE,
    },
    {
        "student_code": "2021CNTT005",
        "full_name": "Hoàng Thị Uyên",
        "class_code": "CNTT01",
        "email": "hoangthiuyen@hou.edu.vn",
        "phone": "0901234005",
        "enrollment_year": 2021,
        "status": StudentStatus.ACTIVE,
    },
]

USERS = [
    {
        "username": "admin",
        "email": "admin@hou.edu.vn",
        "password_hash": "$2b$12$LJ3UlMJhCO0t8N9VB0zEYe9.0y8E3p1Xl5Q0j5Kk5E5Q0j5Kk5E5",  # placeholder
        "role": UserRole.ADMIN,
        "is_active": True,
    },
    {
        "username": "gv_nguyen",
        "email": "gvnguyen@hou.edu.vn",
        "password_hash": "$2b$12$LJ3UlMJhCO0t8N9VB0zEYe9.0y8E3p1Xl5Q0j5Kk5E5Q0j5Kk5E5",
        "role": UserRole.GIANG_VIEN,
        "is_active": True,
    },
]

LECTURERS = [
    {
        "lecturer_code": "GV001",
        "full_name": "TS. Nguyễn Văn Giảng",
        "email": "gvnguyen@hou.edu.vn",
        "phone": "0912345678",
        "department": "Khoa CNTT",
        # user_id sẽ được gán sau khi tạo user
    },
]


async def seed():
    print("🌱 Bắt đầu seed data...")

    async with async_session_factory() as session:
        try:
            # Kiểm tra đã có data chưa
            result = await session.execute(text("SELECT COUNT(*) FROM students"))
            count = result.scalar_one()
            if count > 0:
                print(f"⚠️  DB đã có {count} students. Bỏ qua seed.")
                print("   Muốn seed lại? Chạy: make db-reset && make migrate && make seed")
                return

            # ── Tạo Students ──
            for data in STUDENTS:
                session.add(Student(**data))
            print(f"  ✅ Tạo {len(STUDENTS)} students")

            # ── Tạo Users ──
            user_objects = []
            for data in USERS:
                user = User(**data)
                session.add(user)
                user_objects.append(user)
            await session.flush()  # Lấy ID cho users
            print(f"  ✅ Tạo {len(USERS)} users")

            # ── Tạo Lecturers (link với user) ──
            for i, data in enumerate(LECTURERS):
                # Link lecturer với user thứ 2 (gv_nguyen)
                if i < len(user_objects) - 1:
                    data["user_id"] = user_objects[i + 1].id
                session.add(Lecturer(**data))
            print(f"  ✅ Tạo {len(LECTURERS)} lecturers")

            await session.commit()
            print("🎉 Seed data thành công!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Lỗi seed: {e}")
            raise
        finally:
            await session.close()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
