
from supabase import Client

from app.core.errors import AppError
from app.modules.cashflow_categories.repository import CategoryRepository
from app.modules.cashflow_categories.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
)


class CategoryService:
    def __init__(self, db: Client) -> None:
        self.repo = CategoryRepository(db)

    def list(self) -> list[CategoryOut]:
        return [CategoryOut(**row) for row in self.repo.list()]

    def get(self, category_id: str) -> CategoryOut | None:
        row = self.repo.get(category_id)
        return CategoryOut(**row) if row else None

    def create(self, data: CategoryCreate) -> CategoryOut:
        payload = data.model_dump()
        payload["direction"] = data.direction.value
        return CategoryOut(**self.repo.create(payload))

    def update(self, category_id: str, data: CategoryUpdate) -> CategoryOut:
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise AppError("No fields to update")
        if "direction" in payload and data.direction is not None:
            payload["direction"] = data.direction.value
        row = self.repo.update(category_id, payload)
        if not row:
            raise AppError("Category not found", 404)
        return CategoryOut(**row)

    def delete(self, category_id: str) -> None:
        if self.repo.delete(category_id) == 0:
            raise AppError("Category not found", 404)