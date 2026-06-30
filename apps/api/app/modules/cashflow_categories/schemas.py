from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CategoryDirection(StrEnum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"
    BOTH = "BOTH"


class CategoryCreate(BaseModel):
    name: str
    direction: CategoryDirection
    parent_category_id: str | None = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = None
    direction: CategoryDirection | None = None
    parent_category_id: str | None = None
    is_active: bool | None = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    parent_category_id: str | None = None
    name: str
    direction: str
    is_active: bool
    created_at: str