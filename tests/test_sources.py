"""Tests for /api/sources."""

import pytest
import respx
import httpx

from tests.conftest import MOCK_SOURCES_PAYLOAD


@pytest.mark.asyncio
@respx.mock
async def test_sources_success(async_client):
    """Happy-path: returns list of sources."""
    respx.get("https://newsapi.org/v2/top-headlines/sources").mock(
        return_value=httpx.Response(200, json=MOCK_SOURCES_PAYLOAD)
    )

    response = await async_client.get("/api/sources")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert len(body["sources"]) == 1
    assert body["sources"][0]["id"] == "bbc-news"


@pytest.mark.asyncio
@respx.mock
async def test_sources_category_filter(async_client):
    """Category filter is forwarded to NewsAPI."""
    route = respx.get("https://newsapi.org/v2/top-headlines/sources").mock(
        return_value=httpx.Response(200, json=MOCK_SOURCES_PAYLOAD)
    )

    await async_client.get("/api/sources", params={"category": "technology"})

    assert "category=technology" in str(route.calls[0].request.url)


@pytest.mark.asyncio
@respx.mock
async def test_sources_country_and_language(async_client):
    """Country and language filters are forwarded."""
    route = respx.get("https://newsapi.org/v2/top-headlines/sources").mock(
        return_value=httpx.Response(200, json=MOCK_SOURCES_PAYLOAD)
    )

    await async_client.get("/api/sources", params={"country": "gb", "language": "en"})

    url_str = str(route.calls[0].request.url)
    assert "country=gb" in url_str
    assert "language=en" in url_str


@pytest.mark.asyncio
@respx.mock
async def test_sources_upstream_error(async_client):
    """Source-not-found error returns 404."""
    respx.get("https://newsapi.org/v2/top-headlines/sources").mock(
        return_value=httpx.Response(
            200,
            json={"status": "error", "code": "sourceDoesNotExist", "message": "Not found."},
        )
    )

    response = await async_client.get("/api/sources")
    assert response.status_code == 404
