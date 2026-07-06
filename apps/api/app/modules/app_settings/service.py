from supabase import Client

from app.core.errors import AppError
from app.modules.app_settings.repository import AppSettingRepository
from app.modules.app_settings.schemas import AppSettingOut, AppSettingUpsert


class AppSettingService:
    def __init__(self, db: Client) -> None:
        self.repo = AppSettingRepository(db)

    def list(self) -> list[AppSettingOut]:
        return [AppSettingOut(**row) for row in self.repo.list()]

    def get_by_key(self, key: str) -> AppSettingOut | None:
        row = self.repo.get_by_key(key)
        return AppSettingOut(**row) if row else None

    def upsert(self, data: AppSettingUpsert, actor_id: str) -> AppSettingOut:
        self._validate_setting(data)
        existing = self.repo.get_by_key(data.key)
        if existing:
            row = self.repo.update(
                existing["id"], {"value": data.value, "updated_by": actor_id}
            )
            if row is None:
                raise AppError("Setting not found", 404)
        else:
            row = self.repo.create(
                {"key": data.key, "value": data.value, "updated_by": actor_id}
            )
        return AppSettingOut(**row)

    def _validate_setting(self, data: AppSettingUpsert) -> None:
        if (
            data.key == "attachment_threshold_enabled"
            and data.value.lower() not in {"true", "false"}
        ):
            raise AppError("attachment_threshold_enabled must be true or false", 422)
        if data.key == "attachment_threshold_amount":
            try:
                amount = float(data.value)
            except (TypeError, ValueError) as exc:
                raise AppError(
                    "attachment_threshold_amount must be numeric", 422
                ) from exc
            if amount <= 0:
                raise AppError("attachment_threshold_amount must be positive", 422)
