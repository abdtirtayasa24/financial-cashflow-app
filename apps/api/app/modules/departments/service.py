
from supabase import Client

from app.core.errors import AppError
from app.modules.departments.repository import DepartmentRepository
from app.modules.departments.schemas import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
)


class DepartmentService:
    def __init__(self, db: Client) -> None:
        self.repo = DepartmentRepository(db)

    def list(self) -> list[DepartmentOut]:
        return [DepartmentOut(**row) for row in self.repo.list()]

    def get(self, department_id: str) -> DepartmentOut | None:
        row = self.repo.get(department_id)
        return DepartmentOut(**row) if row else None

    def create(self, data: DepartmentCreate) -> DepartmentOut:
        row = self.repo.create(data.model_dump())
        return DepartmentOut(**row)

    def update(self, department_id: str, data: DepartmentUpdate) -> DepartmentOut:
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise AppError("No fields to update")
        row = self.repo.update(department_id, payload)
        if not row:
            raise AppError("Department not found", 404)
        return DepartmentOut(**row)

    def delete(self, department_id: str) -> None:
        if self.repo.delete(department_id) == 0:
            raise AppError("Department not found", 404)