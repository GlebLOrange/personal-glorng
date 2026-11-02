"""Path containment for file-share disk paths."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.core.exceptions import NotFoundError
from app.db.documents.fileshare import SharedFile
from app.db.registry import DatabaseRegistry
from app.services import fileshare as fileshare_svc
from tests.factories import create_user


def test_resolve_share_path_rejects_traversal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shares = tmp_path / "shares"
    shares.mkdir()
    (tmp_path / "secret.txt").write_bytes(b"leak")
    monkeypatch.setattr(fileshare_svc, "_shares_dir", lambda: shares)

    assert fileshare_svc._resolve_share_path("ok.txt") == (shares / "ok.txt").resolve()
    assert fileshare_svc._resolve_share_path("../secret.txt") is None
    assert fileshare_svc._resolve_share_path("nested/../../secret.txt") is None


@pytest.mark.asyncio
async def test_get_by_code_rejects_escaped_file_path(
    registry: DatabaseRegistry,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shares = tmp_path / "shares"
    shares.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"should-not-serve")
    monkeypatch.setattr(fileshare_svc, "_shares_dir", lambda: shares)

    user = await create_user(registry)
    shared = SharedFile(
        code="esc001",
        original_filename="outside.txt",
        file_path="../outside.txt",
        file_size=outside.stat().st_size,
        content_type="text/plain",
        downloads=0,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
        created_by=user.id,
    )
    assert registry.files is not None
    await registry.files.insert(shared)

    with pytest.raises(NotFoundError):
        await fileshare_svc.get_by_code(registry, code="esc001")
