import io
from datetime import UTC, datetime, timedelta

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
async def test_download_invalid_code_chars(client: AsyncClient) -> None:
    resp = await client.get("/f/bad!code")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_download_sanitized_content_disposition(
    client: AsyncClient, auth_client: AsyncClient
) -> None:
    from app.core.utils import attachment_content_disposition

    upload_resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file('report "Q1".pdf', b"pdf data", "application/pdf"),
    )
    code = upload_resp.json()["code"]
    filename = upload_resp.json()["original_filename"]
    expected = attachment_content_disposition(filename)

    resp = await client.get(f"/f/{code}")
    assert resp.status_code == 200
    assert resp.headers.get("content-disposition") == expected


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
async def test_upload_blocked_double_extension(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file("payload.html.txt", b"hello", "text/plain"),
    )
    assert resp.status_code == 400
    assert ".html" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_delete_file_other_user_forbidden(
    auth_client: AsyncClient,
    db: AsyncSession,
) -> None:
    upload_resp = await auth_client.post(
        "/api/tools/file-share",
        files=_make_file("private.txt", b"secret"),
    )
    file_id = upload_resp.json()["id"]

    other = await create_user(db, email="other@example.com")

    from app.core.auth import create_access_token

    token = create_access_token(str(other.public_id))
    resp = await auth_client.delete(
        f"/api/tools/file-share/{file_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


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


@pytest.mark.asyncio
async def test_cleanup_expired_removes_row_and_disk_file(db: AsyncSession) -> None:
    user = await create_user(db)
    shares_dir = fileshare_svc._shares_dir()
    shares_dir.mkdir(parents=True, exist_ok=True)
    disk_name = "exp002_old.txt"
    (shares_dir / disk_name).write_bytes(b"stale")

    expired = SharedFile(
        code="exp002",
        original_filename="old.txt",
        file_path=disk_name,
        file_size=5,
        content_type="text/plain",
        downloads=0,
        expires_at=datetime(2020, 1, 1, tzinfo=UTC),
        created_by=user.id,
    )
    active = SharedFile(
        code="act002",
        original_filename="new.txt",
        file_path="act002_new.txt",
        file_size=3,
        content_type="text/plain",
        downloads=0,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        created_by=user.id,
    )
    db.add_all([expired, active])
    await db.commit()

    stats = await fileshare_svc.cleanup_expired(db)
    await db.commit()

    assert stats == {"deleted_rows": 1, "deleted_files": 1, "errors": 0}
    assert not (shares_dir / disk_name).exists()

    result = await db.get(SharedFile, expired.id)
    assert result is None
    assert await db.get(SharedFile, active.id) is not None
