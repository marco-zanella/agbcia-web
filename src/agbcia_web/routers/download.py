"""``GET /api/download/{token}`` and its QR-code companion."""

from __future__ import annotations

from io import BytesIO

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from agbcia_web.deps import get_result_store
from agbcia_web.store import ResultStore, StoredResult

router = APIRouter()


async def _get_entry(token: str, store: ResultStore) -> StoredResult:
    entry = await store.get(token)
    if entry is None:
        raise HTTPException(status_code=404, detail="no such download (expired or unknown token)")
    return entry


@router.get("/api/download/{token}")
async def download(token: str, store: ResultStore = Depends(get_result_store)) -> Response:
    entry = await _get_entry(token, store)
    return Response(
        content=entry.data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{entry.filename}"'},
    )


@router.get("/api/download/{token}/qr")
async def download_qr(
    token: str,
    request: Request,
    store: ResultStore = Depends(get_result_store),
) -> Response:
    await _get_entry(token, store)
    download_url = str(request.url_for("download", token=token))
    image = qrcode.make(download_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")
