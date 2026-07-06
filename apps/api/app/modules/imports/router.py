from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from supabase import Client

from app.core.auth import get_current_user
from app.core.models import CurrentUser
from app.core.supabase_client import get_supabase_client
from app.modules.imports.schemas import ImportTransactionsOut
from app.modules.imports.service import MAX_IMPORT_FILE_BYTES, TransactionImportService

router = APIRouter(prefix="/import", tags=["Import"])

CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


@router.post("/transactions", response_model=ImportTransactionsOut)
async def import_transactions(
    db: Annotated[Client, Depends(get_supabase_client)],
    user: CurrentUserDep,
    file: Annotated[UploadFile, File()],
) -> ImportTransactionsOut:
    content = await _read_limited(file)
    return TransactionImportService(db).import_file(
        filename=file.filename or "", content=content, user=user
    )


async def _read_limited(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(1024 * 1024):
        total += len(chunk)
        if total > MAX_IMPORT_FILE_BYTES:
            allowed = max(MAX_IMPORT_FILE_BYTES + 1 - (total - len(chunk)), 0)
            chunks.append(chunk[:allowed])
            break
        chunks.append(chunk)
    return b"".join(chunks)
