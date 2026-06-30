from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Role(StrEnum):
    EMPLOYEE = "EMPLOYEE"
    DEPARTMENT_MANAGER = "DEPARTMENT_MANAGER"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    MANAGEMENT = "MANAGEMENT"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class CurrentUser(BaseModel):
    """The authenticated user resolved on each protected request."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    role: Role
    department_id: str | None = None
    full_name: str
    status: UserStatus
    email: str | None = None