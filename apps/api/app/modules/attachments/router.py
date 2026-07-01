from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from supabase import Client

from app.core.auth import get_current_user
from app.core.config import Settings, get_settings
from app.core.models import CurrentUser
from app.core.supabase_client import get_supabase_client
from app.modules.attachments import storage
from app.modules.attachments.schemas import AttachmentOut
from app.modules.attachments.service import AttachmentService
from app.modules.transactions.service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Attachments"])

UserDep = Annotated[CurrentUser, Depends(get_current_user)]
DbDep = Annotated[Client, Depends(get_supabase_client)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get(
    "/{transaction_id}/attachments",
    response_model=list[AttachmentOut],
)
async def list_attachments(
    transaction_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> list[AttachmentOut]:
    TransactionService(db, settings).get_raw_for_view(transaction_id, user)
    return AttachmentService(db, settings).list_for_transaction(transaction_id)


@router.post(
    "/{transaction_id}/attachments",
    response_model=AttachmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    transaction_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
    file: Annotated[UploadFile, File()],
) -> AttachmentOut:
    tx_service = TransactionService(db, settings)
    tx = tx_service.get_raw_for_mutation(transaction_id, user)
    return await AttachmentService(db, settings).upload(tx, file, user)


@router.get(
    "/{transaction_id}/attachments/{attachment_id}/download",
)
async def download_attachment(
    transaction_id: str,
    attachment_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> FileResponse:
    TransactionService(db, settings).get_raw_for_view(transaction_id, user)
    att = AttachmentService(db, settings).get(attachment_id, transaction_id)
    path = storage.absolute_path(att["relative_path"], settings)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment file not found",
        )
    return FileResponse(
        path,
        media_type=att["mime_type"],
        filename=att["original_file_name"],
    )


@router.delete(
    "/{transaction_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_attachment(
    transaction_id: str,
    attachment_id: str,
    db: DbDep,
    user: UserDep,
    settings: SettingsDep,
) -> None:
    tx_service = TransactionService(db, settings)
    tx = tx_service.get_raw_for_mutation(transaction_id, user)
    AttachmentService(db, settings).delete(attachment_id, tx, user)