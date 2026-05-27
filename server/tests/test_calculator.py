"""Tests for the server-side calculator endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_addition(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator", params={"a": 2, "b": 3, "op": "+"}
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 5


@pytest.mark.asyncio
async def test_subtraction(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator", params={"a": 10, "b": 4, "op": "-"}
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 6


@pytest.mark.asyncio
async def test_multiplication(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator", params={"a": 7, "b": 6, "op": "*"}
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 42


@pytest.mark.asyncio
async def test_division(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator", params={"a": 15, "b": 4, "op": "/"}
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 3.75


@pytest.mark.asyncio
async def test_division_by_zero(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator", params={"a": 1, "b": 0, "op": "/"}
    )
    assert resp.status_code == 422
    assert "zero" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_invalid_operator(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/calculator", params={"a": 1, "b": 2, "op": "^"}
    )
    assert resp.status_code == 422
    assert "operator" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unauthorized(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/calculator", params={"a": 1, "b": 2, "op": "+"}
    )
    assert resp.status_code == 401
