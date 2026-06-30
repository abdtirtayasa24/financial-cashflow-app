from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.models import Role, UserStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str
    role: Role
    department_id: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: Role | None = None
    department_id: str | None = None
    status: UserStatus | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    email: str | None = None
    full_name: str
    role: Role
    department_id: str | None = None
    status: UserStatus
    created_at: str