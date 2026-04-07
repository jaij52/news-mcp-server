"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from news_mcp.config import Settings, get_settings
from news_mcp.main import create_app


@pytest.fixture()
def test_settings() -> Settings:
    """Settings with a fake API key — real network calls are always mocked."""
    return Settings(
        news_api_key="test-key-000",
        news_api_base_url="https://newsapi.org/v2",
        app_env="test",
        log_level="WARNING",
    )


@pytest.fixture()
def app(test_settings: Settings):
    """FastAPI app with the test settings injected."""
    application = create_app()
    application.dependency_overrides[get_settings] = lambda: test_settings
    return application


@pytest.fixture()
async def async_client(app):
    """Async HTTPX client backed by the test app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


# ---------------------------------------------------------------------------
# Reusable NewsAPI mock payloads
# ---------------------------------------------------------------------------

MOCK_ARTICLES_PAYLOAD = {
    "status": "ok",
    "totalResults": 2,
    "articles": [
        {
            "source": {"id": "bbc-news", "name": "BBC News"},
            "author": "BBC Journalist",
            "title": "Breaking: Something happened",
            "description": "A short description.",
            "url": "https://bbc.com/news/1",
            "urlToImage": "https://bbc.com/img/1.jpg",
            "publishedAt": "2026-04-06T10:00:00Z",
            "content": "Full content here...",
        },
        {
            "source": {"id": "cnn", "name": "CNN"},
            "author": None,
            "title": "Another story",
            "description": None,
            "url": "https://cnn.com/story/2",
            "urlToImage": None,
            "publishedAt": "2026-04-06T09:00:00Z",
            "content": None,
        },
    ],
}

MOCK_SOURCES_PAYLOAD = {
    "status": "ok",
    "sources": [
        {
            "id": "bbc-news",
            "name": "BBC News",
            "description": "Use BBC News for up-to-the-minute news.",
            "url": "https://www.bbc.co.uk/news",
            "category": "general",
            "language": "en",
            "country": "gb",
        }
    ],
}
