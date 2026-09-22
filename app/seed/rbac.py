
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission


PERMISSIONS = [
    ("user.view", "View users"),
    ("user.create", "Create users"),
    ("user.edit", "Edit users"),
    ("user.delete", "Delete users"),

    ("role.view", "View roles"),
    ("role.create", "Create roles"),
    ("role.edit", "Edit roles"),
    ("role.delete", "Delete roles"),

    ("project.view", "View projects"),
    ("project.create", "Create projects"),
    ("project.edit", "Edit projects"),
    ("project.delete", "Delete projects"),
    ("project.manage_members", "Manage project members"),
]


async def seed_rbac(
    db: AsyncSession,
    organization_id,
):
    # -------------------------
    # 1. Create permissions
    # -------------------------

    for name, description in PERMISSIONS:
        result = await db.execute(
            select(Permission).where(
                Permission.name == name
            )
        )

        permission = result.scalar_one_or_none()

        if permission is None:
            permission = Permission(
                name=name,
                description=description,
            )

            db.add(permission)

    await db.flush()

    # -------------------------
    # 2. Get/Create ADMIN role
    # -------------------------

    result = await db.execute(
        select(Role).where(
            Role.organization_id == organization_id,
            Role.name == "ADMIN",
        )
    )

    admin_role = result.scalar_one_or_none()

    if admin_role is None:
        admin_role = Role(
            organization_id=organization_id,
            name="ADMIN",
            description="Organization administrator",
            is_active=True,
        )

        db.add(admin_role)
        await db.flush()

    # -------------------------
    # 3. Give ADMIN all permissions
    # -------------------------

    result = await db.execute(
        select(Permission)
    )

    permissions = result.scalars().all()

    for permission in permissions:
        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == admin_role.id,
                RolePermission.permission_id == permission.id,
            )
        )

        existing = result.scalar_one_or_none()

        if existing is None:
            db.add(
                RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                )
            )

    await db.commit()

