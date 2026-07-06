from pydantic import BaseModel, ConfigDict


class ImportRowError(BaseModel):
    row_number: int
    message: str


class ImportedTransactionOut(BaseModel):
    id: str
    transaction_no: str


class ImportTransactionsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_rows: int
    imported_count: int
    failed_count: int
    imported: list[ImportedTransactionOut]
    errors: list[ImportRowError]
