from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SubmissionMode(StrEnum):
    AUTO_SUBMIT = "AUTO_SUBMIT"
    DRAFT = "DRAFT"


class RecurrenceFrequency(StrEnum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class TemplateDirection(StrEnum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"


class RecurringTemplateBase(BaseModel):
    department_id: str
    category_id: str
    cash_account_id: str
    payment_method_id: str = Field(min_length=1)
    direction: TemplateDirection
    amount: float = Field(gt=0)
    counterparty_name: str | None = None
    reference_no: str | None = None
    description: str | None = None
    submission_mode: SubmissionMode
    frequency: RecurrenceFrequency
    interval: int = Field(default=1, ge=1)
    next_run_date: str
    end_date: str | None = None

    @field_validator("next_run_date", "end_date")
    @classmethod
    def valid_iso_date(cls, value: str | None) -> str | None:
        if value is None:
            return None
        from datetime import date

        date.fromisoformat(value)
        return value

    @model_validator(mode="after")
    def end_date_not_before_next_run(self) -> "RecurringTemplateBase":
        if self.end_date and self.end_date < self.next_run_date:
            raise ValueError("end_date must be on or after next_run_date")
        return self


class RecurringTemplateCreate(RecurringTemplateBase):
    pass


class RecurringTemplateUpdate(BaseModel):
    department_id: str | None = None
    category_id: str | None = None
    cash_account_id: str | None = None
    payment_method_id: str | None = None
    direction: TemplateDirection | None = None
    amount: float | None = Field(default=None, gt=0)
    counterparty_name: str | None = None
    reference_no: str | None = None
    description: str | None = None
    submission_mode: SubmissionMode | None = None
    frequency: RecurrenceFrequency | None = None
    interval: int | None = Field(default=None, ge=1)
    next_run_date: str | None = None
    end_date: str | None = None

    @field_validator("next_run_date", "end_date")
    @classmethod
    def valid_iso_date(cls, value: str | None) -> str | None:
        if value is None:
            return None
        from datetime import date

        date.fromisoformat(value)
        return value


class RecurringTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    department_id: str
    category_id: str
    cash_account_id: str
    payment_method_id: str | None = None
    direction: str
    amount: float
    currency: str = "IDR"
    counterparty_name: str | None = None
    reference_no: str | None = None
    description: str | None = None
    submission_mode: str
    frequency: str
    interval: int
    next_run_date: str
    end_date: str | None = None
    is_active: bool
    created_by: str
    created_at: str
    updated_at: str
