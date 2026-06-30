from pydantic import BaseModel, ConfigDict


class AppSettingUpsert(BaseModel):
    key: str
    value: str


class AppSettingUpdate(BaseModel):
    value: str


class AppSettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    key: str
    value: str
    updated_by: str | None = None
    updated_at: str
    created_at: str