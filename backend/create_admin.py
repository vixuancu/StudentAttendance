"""
Tạo nhanh tài khoản admin để test API.

Chạy từ thư mục backend:
    python create_admin.py
"""

import asyncio

from sqlalchemy import select

from src.db.base import Base
from src.db.models.role import Role
from src.db.models.user import User
from src.db import models  # noqa: F401 - đảm bảo tất cả model được register
from src.db.session import async_session_factory, engine
from src.utils.security import hash_password


ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@edu.vn"
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "System Admin"
DEFAULT_ROLES = ["admin", "giao_vu", "giang_vien"]


async def create_or_update_admin() -> None:
    # Tạo bảng nếu DB đang trống (dev bootstrap)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        existing_roles_result = await session.execute(
            select(Role).where(Role.role_name.in_(DEFAULT_ROLES))
        )
        existing_roles = {role.role_name: role for role in existing_roles_result.scalars().all()}

        for role_name in DEFAULT_ROLES:
            if role_name not in existing_roles:
                role = Role(role_name=role_name, is_cancel=False)
                session.add(role)
                await session.flush()
                existing_roles[role_name] = role

        admin_role = existing_roles["admin"]

        user_result = await session.execute(
            select(User).where(User.username == ADMIN_USERNAME)
        )
        admin_user = user_result.scalar_one_or_none()

        if admin_user is None:
            admin_user = User(
                username=ADMIN_USERNAME,
                password=hash_password(ADMIN_PASSWORD),
                full_name=ADMIN_FULL_NAME,
                email=ADMIN_EMAIL,
                gender=None,
                birth_of_date=None,
                role_id=admin_role.id,
                is_online=False,
                is_cancel=False,
            )
            session.add(admin_user)
            action = "created"
        else:
            admin_user.password = hash_password(ADMIN_PASSWORD)
            admin_user.email = ADMIN_EMAIL
            admin_user.full_name = ADMIN_FULL_NAME
            admin_user.role_id = admin_role.id
            admin_user.is_cancel = False
            action = "updated"

        await session.commit()

    print("Admin account", action)
    print("username:", ADMIN_USERNAME)
    print("password:", ADMIN_PASSWORD)


if __name__ == "__main__":
    asyncio.run(create_or_update_admin())
