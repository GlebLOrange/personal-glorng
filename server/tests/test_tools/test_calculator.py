"""Tests for the server-side calculator endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_calculator_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/calculator",
        json={"a": 1, "b": 2, "op": "+"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 3


@pytest.mark.asyncio
async def test_calculator_add(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        json={"a": 10, "b": 5, "op": "+"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 15


@pytest.mark.asyncio
async def test_calculator_subtract(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        json={"a": 10, "b": 3, "op": "-"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 7


@pytest.mark.asyncio
async def test_calculator_multiply(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        json={"a": 4, "b": 5, "op": "*"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 20


@pytest.mark.asyncio
async def test_calculator_divide(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        json={"a": 15, "b": 4, "op": "/"},
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 3.75


@pytest.mark.asyncio
async def test_calculator_divide_by_zero(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        json={"a": 10, "b": 0, "op": "/"},
    )
    assert resp.status_code == 422
    assert "zero" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_calculator_invalid_operator(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        json={"a": 1, "b": 2, "op": "^"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_calculator_nan_rejected(auth_client: AsyncClient) -> None:
    # httpx json= cannot encode NaN; send Python-json NaN that FastAPI still parses.
    resp = await auth_client.post(
        "/api/tools/calculator",
        content=b'{"a":NaN,"b":1,"op":"+"}',
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_calculator_infinity_rejected(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        content=b'{"a":Infinity,"b":1,"op":"+"}',
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_calculator_overflow_rejected(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator",
        json={"a": 1e16, "b": 1, "op": "+"},
    )
    assert resp.status_code == 422
    assert "must be between" in resp.json()["detail"]
