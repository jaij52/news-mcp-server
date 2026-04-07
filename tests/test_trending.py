"""Tests for /api/trending."""

import pytest
import respx
import httpx

from tests.conftest import MOCK_ARTICLES_PAYLOAD


@pytest.mark.asyncio
@respx.mock
async def test_trending_success(async_client):
    """Happy-path: trending returns popular articles."""
    respx.get("https://newsapi.org/v2/everything").mock(
        return_value=httpx.Response(200, json=MOCK_ARTICLES_PAYLOAD)
    )

    response = await async_client.get("/api/trending")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert len(body["articles"]) == 2


@pytest.mark.asyncio
@respx.mock
async def test_trending_popularity_sort(async_client):
    """Trending endpoint uses sortBy=popularity."""
    route = respx.get("https://newsapi.org/v2/everything").mock(
        return_value=httpx.Response(200, json=MOCK_ARTICLES_PAYLOAD)
    )

    await async_client.get("/api/trending", params={"language": "en"})

    assert "sortBy=popularity" in str(route.calls[0].request.url)


@pytest.mark.asyncio
@respx.mock
async def test_trending_language_filter(async_client):
    """Language parameter is forwarded to NewsAPI."""
    route = respx.get("https://newsapi.org/v2/everything").mock(
        return_value=httpx.Response(200, json=MOCK_ARTICLES_PAYLOAD)
    )

    await async_client.get("/api/trending", params={"language": "de"})

    assert "language=de" in str(route.calls[0].request.url)
