"""Tests for /api/search."""

import pytest
import respx
import httpx

from tests.conftest import MOCK_ARTICLES_PAYLOAD


@pytest.mark.asyncio
@respx.mock
async def test_search_success(async_client):
    """Happy-path: keyword search returns articles."""
    respx.get("https://newsapi.org/v2/everything").mock(
        return_value=httpx.Response(200, json=MOCK_ARTICLES_PAYLOAD)
    )

    response = await async_client.get("/api/search", params={"q": "climate change"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert len(body["articles"]) == 2


@pytest.mark.asyncio
async def test_search_missing_q(async_client):
    """Missing required 'q' parameter returns 422."""
    response = await async_client.get("/api/search")
    assert response.status_code == 422


@pytest.mark.asyncio
@respx.mock
async def test_search_date_range(async_client):
    """Date range parameters are forwarded to NewsAPI."""
    route = respx.get("https://newsapi.org/v2/everything").mock(
        return_value=httpx.Response(200, json=MOCK_ARTICLES_PAYLOAD)
    )

    await async_client.get(
        "/api/search",
        params={"q": "AI", "from": "2026-04-01", "to": "2026-04-06"},
    )

    url_str = str(route.calls[0].request.url)
    assert "from=2026-04-01" in url_str
    assert "to=2026-04-06" in url_str


@pytest.mark.asyncio
@respx.mock
async def test_search_rate_limited(async_client):
    """Rate-limit error from NewsAPI returns 429."""
    respx.get("https://newsapi.org/v2/everything").mock(
        return_value=httpx.Response(
            200,
            json={"status": "error", "code": "rateLimited", "message": "Rate limited."},
        )
    )

    response = await async_client.get("/api/search", params={"q": "test"})
    assert response.status_code == 429
