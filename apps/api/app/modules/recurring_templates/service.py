from typing import Any

from supabase import Client

from app.core.errors import AppError
from app.core.models import CurrentUser, Role
from app.modules.recurring_templates.repository import RecurringTemplateRepository
from app.modules.recurring_templates.schemas import (
    RecurringTemplateCreate,
    RecurringTemplateOut,
    RecurringTemplateUpdate,
    SubmissionMode,
)

_VIEW_ALL = {Role.FINANCE_ADMIN, Role.MANAGEMENT}


class RecurringTemplateService:
    def __init__(self, db: Client) -> None:
        self.repo = RecurringTemplateRepository(db)

    def list(self, user: CurrentUser) -> list[RecurringTemplateOut]:
        filters: dict[str, Any] = {}
        if user.role in _VIEW_ALL:
            pass
        elif user.role in {Role.EMPLOYEE, Role.DEPARTMENT_MANAGER}:
            if not user.department_id:
                raise AppError("forbidden", 403)
            filters["department_id"] = user.department_id
        else:
            raise AppError("forbidden", 403)
        return [RecurringTemplateOut(**row) for row in self.repo.list(filters)]

    def get(self, template_id: str, user: CurrentUser) -> RecurringTemplateOut:
        row = self.repo.get(template_id)
        if not row or not self._can_view(row, user):
            raise AppError("Template not found", 404)
        return RecurringTemplateOut(**row)

    def create(
        self, data: RecurringTemplateCreate, user: CurrentUser
    ) -> RecurringTemplateOut:
        if user.role not in {Role.FINANCE_ADMIN, Role.MANAGEMENT, Role.EMPLOYEE}:
            raise AppError("forbidden", 403)
        self._require_create_allowed(data, user)
        self._validate_references(data.model_dump())
        payload = data.model_dump()
        payload.update({"currency": "IDR", "is_active": True, "created_by": user.id})
        row = self.repo.create(payload)
        return RecurringTemplateOut(**row)

    def update(
        self, template_id: str, data: RecurringTemplateUpdate, user: CurrentUser
    ) -> RecurringTemplateOut:
        row = self.repo.get(template_id)
        if not row or not self._can_view(row, user):
            raise AppError("Template not found", 404)
        if not row["is_active"]:
            raise AppError("Only active templates can be edited", 409)
        if user.role not in {Role.FINANCE_ADMIN, Role.MANAGEMENT, Role.EMPLOYEE}:
            raise AppError("forbidden", 403)
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise AppError("No fields to update", 422)
        merged = {**row, **payload}
        self._require_update_allowed(row, merged, user)
        self._validate_dates(merged)
        self._validate_references(merged)
        updated = self.repo.update(template_id, payload)
        if not updated:
            raise AppError("Template not found", 404)
        return RecurringTemplateOut(**updated)

    def deactivate(self, template_id: str, user: CurrentUser) -> RecurringTemplateOut:
        row = self.repo.get(template_id)
        if not row or not self._can_view(row, user):
            raise AppError("Template not found", 404)
        if user.role not in {Role.FINANCE_ADMIN, Role.MANAGEMENT, Role.EMPLOYEE}:
            raise AppError("forbidden", 403)
        self._require_update_allowed(row, row, user)
        updated = self.repo.update(template_id, {"is_active": False})
        if not updated:
            raise AppError("Template not found", 404)
        return RecurringTemplateOut(**updated)

    def _can_view(self, row: dict[str, Any], user: CurrentUser) -> bool:
        if user.role in _VIEW_ALL:
            return True
        if user.role in {Role.EMPLOYEE, Role.DEPARTMENT_MANAGER}:
            return row.get("department_id") == user.department_id
        return False

    def _require_create_allowed(
        self, data: RecurringTemplateCreate, user: CurrentUser
    ) -> None:
        if user.role in {Role.FINANCE_ADMIN, Role.MANAGEMENT}:
            return
        if user.role == Role.EMPLOYEE:
            if not user.department_id or data.department_id != user.department_id:
                raise AppError(
                    "Employees can only create templates for own department", 403
                )
            if data.submission_mode == SubmissionMode.AUTO_SUBMIT:
                raise AppError("Employees cannot create auto-submit templates", 403)
            return
        raise AppError("forbidden", 403)

    def _require_update_allowed(
        self, original: dict[str, Any], merged: dict[str, Any], user: CurrentUser
    ) -> None:
        if user.role in {Role.FINANCE_ADMIN, Role.MANAGEMENT}:
            return
        if user.role == Role.EMPLOYEE:
            if original.get("created_by") != user.id:
                raise AppError("forbidden", 403)
            if (
                not user.department_id
                or merged.get("department_id") != user.department_id
            ):
                raise AppError("Employees can only manage own department templates", 403)
            if merged.get("submission_mode") == SubmissionMode.AUTO_SUBMIT.value:
                raise AppError("Employees cannot manage auto-submit templates", 403)
            return
        raise AppError("forbidden", 403)

    def _validate_dates(self, values: dict[str, Any]) -> None:
        if values.get("end_date") and values["end_date"] < values["next_run_date"]:
            raise AppError("end_date must be on or after next_run_date", 422)

    def _validate_references(self, values: dict[str, Any]) -> None:
        refs = (
            ("departments", "department_id", "Department"),
            ("cash_accounts", "cash_account_id", "Cash account"),
            ("payment_methods", "payment_method_id", "Payment method"),
        )
        for table, key, label in refs:
            value = values.get(key)
            if value and not self.repo.exists(table, value):
                raise AppError(f"{label} not found", 422)
        category = self.repo.get_category(str(values.get("category_id") or ""))
        if not category:
            raise AppError("Category not found", 422)
        direction = values.get("direction")
        if category.get("direction") not in {direction, "BOTH"}:
            raise AppError("Category direction is incompatible", 422)
