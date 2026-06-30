
from supabase import Client

from app.core.errors import AppError
from app.core.models import Role, UserStatus
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserOut, UserUpdate


class UserService:
    def __init__(self, db: Client) -> None:
        self.repo = UserRepository(db)

    def list(self) -> list[UserOut]:
        return [UserOut(**row) for row in self.repo.list()]

    def get(self, user_id: str) -> UserOut:
        row = self.repo.get(user_id)
        if not row:
            raise AppError("User not found", 404)
        return UserOut(**row)

    def create(self, data: UserCreate) -> UserOut:
        self._require_department_for_role(data.role, data.department_id)
        auth_id = self.repo.create_auth_user(str(data.email), data.password)
        profile = {
            "id": auth_id,
            "email": str(data.email),
            "full_name": data.full_name,
            "role": data.role.value,
            "department_id": data.department_id,
            "status": UserStatus.ACTIVE.value,
        }
        row = self.repo.create_profile(profile)
        out = UserOut(**row)
        out.email = str(data.email)
        return out

    def update(self, user_id: str, data: UserUpdate) -> UserOut:
        if data.role is not None:
            self._require_department_for_role(data.role, data.department_id)
        payload = data.model_dump(exclude_unset=True)
        if "role" in payload and data.role is not None:
            payload["role"] = data.role.value
        if "status" in payload and data.status is not None:
            payload["status"] = data.status.value
        if not payload:
            raise AppError("No fields to update")
        row = self.repo.update_profile(user_id, payload)
        if not row:
            raise AppError("User not found", 404)
        return UserOut(**row)

    @staticmethod
    def _require_department_for_role(role: Role, department_id: str | None) -> None:
        if role in (Role.EMPLOYEE, Role.DEPARTMENT_MANAGER) and not department_id:
            raise AppError(
                f"{role.value} requires a department_id", 422
            )