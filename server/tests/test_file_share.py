import io
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.shared_file import SharedFile
from app.services import fileshare as fileshare_svc
from tests.factories import create_user


def _make_file(
    name: str = "test.txt",
    content: bytes = b"hello world",
    mime: str = "text/plain",
) -> dict:
    return {"file": (name, io.BytesIO(content), mime)}


@pytest.mark.asyncio
async def test_upload_file(auth_client: AsyncClient) -> None:
    resp = await auth_client.post("/api/tools/file-share", files=_make_file())
    assert resp.status_code == 200
    data = resp.json()
    assert data["original_filename"] == "test.txt"
    assert data["file_size"] == 11
    assert data["content_type"] == "text/plain"
    assert len(data["code"]) == 6
    assert data["downloads"] == 0


@pytest.mark.asyncio
async def test_upload_unauthorized(client: AsyncClient) -> None:
    resp = await client.post("/api/tools/file-share", files=_make_file())
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_files(auth_client: AsyncClient) -> None:
    await auth_client.post("/api/tools/file-share", files=_make_file("a.txt", b"data"))
    resp = await auth_client.get("/api/tools/file-share")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_download_file(client: AsyncClient, auth_client: AsyncClient) -> None:
    upload_resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file("dl.txt", b"download me"),
    )
    code = upload_resp.json()["code"]

    resp = await client.get(f"/f/{code}")
    assert resp.status_code == 200
    assert resp.content == b"download me"
    assert "dl.txt" in resp.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_download_not_found(client: AsyncClient) -> None:
    resp = await client.get("/f/nope42")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_no_filename(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/file-share",
        files={"file": ("", io.BytesIO(b"data"), "text/plain")},
    )
    # FastAPI may return 422 for invalid multipart filename or 400 from our guard.
    assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_upload_blocked_extension(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file("page.html", b"<html></html>", "text/html"),
    )
    assert resp.status_code == 400
    assert ".html" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_upload_blocked_js_extension(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file("app.js", b"alert(1)", "application/javascript"),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_upload_exceeds_size_limit(
    auth_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(fileshare_svc, "MAX_UPLOAD_SIZE", 32)
    resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file("big.bin", b"x" * 33, "application/octet-stream"),
    )
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_download_expired_file(client: AsyncClient, db: AsyncSession) -> None:
    user = await create_user(db)
    shared = SharedFile(
        code="exp001",
        original_filename="old.txt",
        file_path="exp001_old.txt",
        file_size=4,
        content_type="text/plain",
        downloads=0,
        expires_at=datetime(2020, 1, 1, 0, 0, 0),
        created_by=user.id,
    )
    db.add(shared)
    await db.commit()

    shares_dir = fileshare_svc._shares_dir()
    shares_dir.mkdir(parents=True, exist_ok=True)
    (shares_dir / shared.file_path).write_bytes(b"gone")

    resp = await client.get("/f/exp001")
    assert resp.status_code == 410


@pytest.mark.asyncio
async def test_delete_file(auth_client: AsyncClient) -> None:
    upload_resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file("rm.txt", b"bye"),
    )
    file_id = upload_resp.json()["id"]
    resp = await auth_client.delete(f"/api/tools/file-share/{file_id}")
    assert resp.status_code == 200

    list_resp = await auth_client.get("/api/tools/file-share")
    ids = [f["id"] for f in list_resp.json()]
    assert file_id not in ids
