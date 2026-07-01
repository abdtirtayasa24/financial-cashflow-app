from datetime import UTC, datetime
from typing import Any

from fastapi import UploadFile
from supabase import Client

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.models import CurrentUser
from app.modules.attachments import storage
from app.modules.attachments.repository import AttachmentRepository
from app.modules.attachments.schemas import AttachmentOut
from app.modules.attachments.storage import InvalidAttachmentError
from app.modules.transactions.repository import TransactionRepository


class AttachmentService:
    def __init__(self, db: Client, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.repo = AttachmentRepository(db)
        self.tx_repo = TransactionRepository(db)

    def list_for_transaction(self, transaction_id: str) -> list[AttachmentOut]:
        rows = self.repo.list_for_transaction(transaction_id)
        return [AttachmentOut(**r) for r in rows]

    def get(self, attachment_id: str, transaction_id: str) -> dict[str, Any]:
        row = self.repo.get(attachment_id)
        if not row or row["transaction_id"] != transaction_id:
            raise AppError("Attachment not found", 404)
        return row

    async def upload(
        self, transaction: dict[str, Any], upload: UploadFile, user: CurrentUser
    ) -> AttachmentOut:
        try:
            stored = await storage.save_upload(
                upload, transaction["id"], self.settings
            )
        except InvalidAttachmentError as exc:
            raise AppError(exc.message, exc.status_code) from exc

        payload = {
            "transaction_id": transaction["id"],
            "original_file_name": stored.original_file_name,
            "stored_file_name": stored.stored_file_name,
            "relative_path": stored.relative_path,
            "mime_type": stored.mime_type,
            "file_size_bytes": stored.file_size_bytes,
            "checksum_sha256": stored.checksum_sha256,
            "uploaded_by": user.id,
            "uploaded_at": datetime.now(UTC).isoformat(),
        }
        row = self.repo.insert(payload)
        self.tx_repo.insert_audit_log(
            {
                "transaction_id": transaction["id"],
                "actor_user_id": user.id,
                "action": "ATTACHMENT_ADD",
                "old_value": None,
                "new_value": {
                    "attachment_id": row["id"],
                    "original_file_name": stored.original_file_name,
                },
            }
        )
        return AttachmentOut(**row)

    def delete(
        self, attachment_id: str, transaction: dict[str, Any], user: CurrentUser
    ) -> None:
        # Fetch and verify ownership BEFORE deleting, so an attachment from
        # another transaction can never be removed by a user who can mutate
        # only this transaction.
        row = self.repo.get(attachment_id)
        if not row or row["transaction_id"] != transaction["id"]:
            raise AppError("Attachment not found", 404)
        self.repo.delete(attachment_id)
        storage.delete_file(row["relative_path"], self.settings)
        self.tx_repo.insert_audit_log(
            {
                "transaction_id": transaction["id"],
                "actor_user_id": user.id,
                "action": "ATTACHMENT_REMOVE",
                "old_value": {
                    "attachment_id": row["id"],
                    "original_file_name": row["original_file_name"],
                },
                "new_value": None,
            }
        )