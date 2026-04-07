"""Tests for /api/headlines."""

import pytest
import respx
import httpx

from tests.conftest import MOCK_ARTICLES_PAYLOAD


@pytest.mark.asyncio
@respx.mock
async def test_headlines_success(async_client):
    """Happy-path: top headlines returns articles list."""
    respx.get("https://newsapi.org/v2/top-headlines").mock(
        return_value=httpx.Response(200, json=MOCK_ARTICLES_PAYLOAD)
    )

    response = await async_client.get("/api/headlines", params={"country": "us"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["totalResults"] == 2
    assert len(body["articles"]) == 2
    assert body["articles"][0]["title"] == "Breaking: Something happened"


@pytest.mark.asyncio
@respx.mock
async def test_headlines_with_category(async_client):
    """Category parameter is forwarded to NewsAPI."""
    route = respx.get("https://newsapi.org/v2/top-headlines").mock(
        return_value=httpx.Response(200, json=MOCK_ARTICLES_PAYLOAD)
    )

    await async_client.get("/api/headlines", params={"country": "us", "category": "technology"})

    assert "category=technology" in str(route.calls[0].request.url)


@pytest.mark.asyncio
@respx.mock
async def test_headlines_upstream_api_error(async_client):
    """NewsAPI error response maps to appropriate HTTP status."""
    error_payload = {
        "status": "error",
        "code": "apiKeyInvalid",
        "message": "Your API key is invalid.",
    }
    respx.get("https://newsapi.org/v2/top-headlines").mock(
        return_value=httpx.Response(200, json=error_payload)
    )

    response = await async_client.get("/api/headlines")

    assert response.status_code == 401


@pytest.mark.asyncio
@respx.mock
async def test_headlines_timeout(async_client):
    """Timeout from NewsAPI returns 504."""
    respx.get("https://newsapi.org/v2/top-headlines").mock(
        side_effect=httpx.TimeoutException("timed out")
    )

    response = await async_client.get("/api/headlines")

    assert response.status_code == 504
