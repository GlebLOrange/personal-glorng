"""Tests for the server-side password generator endpoint."""

import re

import pytest
from httpx import AsyncClient

_ENDPOINT = "/api/tools/password-generator"
_SYMBOL_RE = re.compile(r"[^\w\s]")
_AMBIGUOUS = set("0O1lI")


@pytest.mark.asyncio
async def test_password_generator_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(_ENDPOINT, json={})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["password"]) == 16
    assert data["length"] == 16


@pytest.mark.asyncio
async def test_password_generator_custom_length(client: AsyncClient) -> None:
    resp = await client.post(_ENDPOINT, json={"length": 24})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["password"]) == 24
    assert data["length"] == 24


@pytest.mark.asyncio
async def test_password_generator_length_out_of_range(client: AsyncClient) -> None:
    resp = await client.post(_ENDPOINT, json={"length": 4})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_password_generator_no_charset_selected(client: AsyncClient) -> None:
    resp = await client.post(
        _ENDPOINT,
        json={
            "uppercase": False,
            "lowercase": False,
            "digits": False,
            "symbols": False,
        },
    )
    assert resp.status_code == 422
    assert "character set" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_password_generator_includes_all_selected_sets(
    client: AsyncClient,
) -> None:
    resp = await client.post(
        _ENDPOINT,
        json={
            "length": 16,
            "uppercase": True,
            "lowercase": True,
            "digits": True,
            "symbols": True,
        },
    )
    assert resp.status_code == 200
    password = resp.json()["password"]
    assert re.search(r"[A-Z]", password)
    assert re.search(r"[a-z]", password)
    assert re.search(r"\d", password)
    assert _SYMBOL_RE.search(password)


@pytest.mark.asyncio
async def test_password_generator_exclude_ambiguous(client: AsyncClient) -> None:
    resp = await client.post(
        _ENDPOINT,
        json={
            "length": 32,
            "uppercase": True,
            "lowercase": True,
            "digits": True,
            "symbols": False,
            "exclude_ambiguous": True,
        },
    )
    assert resp.status_code == 200
    password = resp.json()["password"]
    assert not _AMBIGUOUS.intersection(password)
