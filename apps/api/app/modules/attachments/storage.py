"""VPS local file storage for transaction attachments.

Files are stored under ``UPLOAD_DIR`` (a Docker volume in production) and are
never served by Nginx — only streamed through FastAPI after a permission check.
Only metadata lives in PostgreSQL.
"""

from __future__ import annotations

import hashlib
import uuid
from contextlib import suppress
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings

ALLOWED_EXTENSIONS: dict[str, str] = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
}

# File signature (magic bytes) per allowed MIME type. Used to verify that the
# file contents actually match the claimed type, not just the extension.
MAGIC_SIGNATURES: dict[str, bytes] = {
    "application/pdf": b"%PDF-",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/jpeg": b"\xff\xd8\xff",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class InvalidAttachmentError(Exception):
    """Raised when an uploaded file is rejected (type/size)."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class StoredFile:
    original_file_name: str
    stored_file_name: str
    relative_path: str
    mime_type: str
    file_size_bytes: int
    checksum_sha256: str


def _settings() -> Settings:
    return Settings()


def absolute_path(relative_path: str, settings: Settings | None = None) -> Path:
    base = Path((settings or _settings()).upload_dir)
    return base / relative_path


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def validate_upload(
    filename: str, size_bytes: int, content_type: str | None, data: bytes
) -> tuple[str, str]:
    """Return (extension, mime_type) or raise InvalidAttachmentError.

    Validates the extension, the declared content type (when present), the
    size, and the file magic bytes so a renamed hostile file is rejected.
    """
    ext = _extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidAttachmentError(
            f"File type '{ext or 'unknown'}' is not allowed. "
            "Only PDF, PNG, JPG, and JPEG are accepted."
        )
    expected_mime = ALLOWED_EXTENSIONS[ext]
    if content_type and content_type != expected_mime:
        raise InvalidAttachmentError(
            "File content type does not match its extension."
        )
    if size_bytes <= 0:
        raise InvalidAttachmentError("Uploaded file is empty.")
    if size_bytes > MAX_FILE_SIZE:
        raise InvalidAttachmentError(
            "File exceeds the 10 MB size limit.", status_code=413
        )
    signature = MAGIC_SIGNATURES[expected_mime]
    if not data.startswith(signature):
        raise InvalidAttachmentError("File contents do not match its type.")
    return ext, expected_mime


async def save_upload(
    upload: UploadFile, transaction_id: str, settings: Settings
) -> StoredFile:
    """Read, validate, and persist an uploaded file to VPS local storage."""
    original = upload.filename or "upload"
    data = await upload.read()
    ext, mime_type = validate_upload(original, len(data), upload.content_type, data)

    today = date.today()
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    relative = (
        f"transactions/{today.year}/{today.month:02d}/{transaction_id}/{stored_name}"
    )
    path = absolute_path(relative, settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    return StoredFile(
        original_file_name=original,
        stored_file_name=stored_name,
        relative_path=relative,
        mime_type=mime_type,
        file_size_bytes=len(data),
        checksum_sha256=hashlib.sha256(data).hexdigest(),
    )


def delete_file(relative_path: str, settings: Settings | None = None) -> None:
    path = absolute_path(relative_path, settings)
    with suppress(OSError):
        path.unlink(missing_ok=True)