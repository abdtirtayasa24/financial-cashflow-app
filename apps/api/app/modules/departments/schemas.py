from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str
    code: str
    parent_department_id: str | None = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    parent_department_id: str | None = None
    is_active: bool | None = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    name: str
    code: str
    parent_department_id: str | None = None
    is_active: bool
    created_at: str