from pydantic import BaseModel, ConfigDict


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    transaction_id: str
    original_file_name: str
    stored_file_name: str
    relative_path: str
    mime_type: str
    file_size_bytes: int
    checksum_sha256: str | None = None
    uploaded_by: str
    uploaded_at: str