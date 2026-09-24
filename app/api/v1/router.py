
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.project import router as project_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.roles import router as roles_router
from app.api.v1.role_permissions import router as role_permissions_router
from app.api.v1.user_roles import router as user_roles_router
from app.api.v1.project_member_permissions import (router as project_member_permissions_router,)
from app.api.v1.test_cases import router as test_case_router
from app.api.v1.tags import router as tag_router
from app.api.v1.test_step import router as test_step_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(project_router)

# RBAC
api_router.include_router(permissions_router)
api_router.include_router(roles_router)
api_router.include_router(role_permissions_router)
api_router.include_router(user_roles_router)
api_router.include_router(project_member_permissions_router)
api_router.include_router(tag_router)
api_router.include_router(test_case_router)
api_router.include_router(test_step_router)