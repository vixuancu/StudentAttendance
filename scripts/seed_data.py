"""
Seed data mẫu cho development.
Chạy: make seed  (hoặc: cd backend && python -m scripts.seed_data)
"""

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from src.db.session import async_session_factory, engine
from src.db.models.role import Role
from src.db.models.user import User
from src.db.models.student import Student
from src.utils.security import hash_password


# ── Sample Data ──────────────────────────────────────────────

ROLES = [
    {"role_name": "admin"},
    {"role_name": "giao_vu"},
    {"role_name": "giang_vien"},
]

STUDENTS = [
    {
        "full_name": "Nguyễn Văn An",
        "gender": 1,
        "administrative_class": "CNTT01",
    },
    {
        "full_name": "Trần Thị Bình",
        "gender": 0,
        "administrative_class": "CNTT01",
    },
    {
        "full_name": "Lê Hoàng Cường",
        "gender": 1,
        "administrative_class": "CNTT02",
    },
    {
        "full_name": "Phạm Minh Đức",
        "gender": 1,
        "administrative_class": "CNTT02",
    },
    {
        "full_name": "Hoàng Thị Uyên",
        "gender": 0,
        "administrative_class": "CNTT01",
    },
]


async def seed():
    print("🌱 Bắt đầu seed data...")

    async with async_session_factory() as session:
        try:
            # Kiểm tra đã có data chưa
            result = await session.execute(text("SELECT COUNT(*) FROM roles"))
            count = result.scalar_one()
            if count > 0:
                print(f"⚠️  DB đã có {count} roles. Bỏ qua seed.")
                return

            # ── Tạo Roles ──
            role_objects = []
            for data in ROLES:
                role = Role(**data)
                session.add(role)
                role_objects.append(role)
            await session.flush()
            print(f"  ✅ Tạo {len(ROLES)} roles")

            # ── Tạo Users ──
            from datetime import datetime, timezone
            users_data = [
                {
                    "username": "admin",
                    "password": hash_password("admin123"),
                    "full_name": "Administrator",
                    "email": "admin@hou.edu.vn",
                    "gender": 1,
                    "birth_of_date": datetime(1990, 1, 1, tzinfo=timezone.utc),
                    "role_id": role_objects[0].id,  # admin
                },
                {
                    "username": "gv_nguyen",
                    "password": hash_password("123456"),
                    "full_name": "TS. Nguyễn Văn Giảng",
                    "email": "gvnguyen@hou.edu.vn",
                    "gender": 1,
                    "birth_of_date": datetime(1985, 5, 15, tzinfo=timezone.utc),
                    "role_id": role_objects[2].id,  # giang_vien
                },
            ]
            for data in users_data:
                session.add(User(**data))
            print(f"  ✅ Tạo {len(users_data)} users")

            # ── Tạo Students ──
            for data in STUDENTS:
                session.add(Student(**data))
            print(f"  ✅ Tạo {len(STUDENTS)} students")

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
