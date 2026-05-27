import io

import pytest
from httpx import AsyncClient


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
