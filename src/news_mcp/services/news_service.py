"""Business logic for all NewsAPI.org interactions."""

import logging
from typing import Any

import httpx
from fastapi import HTTPException

from news_mcp.config import Settings

logger = logging.getLogger(__name__)

_NEWSAPI_ERROR_MAP: dict[str, int] = {
    "apiKeyDisabled": 401,
    "apiKeyExhausted": 429,
    "apiKeyInvalid": 401,
    "apiKeyMissing": 401,
    "parameterInvalid": 422,
    "parametersMissing": 422,
    "rateLimited": 429,
    "sourcesTooMany": 422,
    "sourceDoesNotExist": 404,
    "unexpectedError": 502,
}


class NewsService:
    """Thin async wrapper around the NewsAPI.org REST API."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.news_api_base_url.rstrip("/")
        self._headers = {
            "X-Api-Key": settings.news_api_key,
            "User-Agent": "news-mcp-server/0.1",
        }

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a GET request against NewsAPI and return the JSON body.

        Raises HTTPException with an appropriate status code on any error.
        """
        url = f"{self._base_url}{path}"
        # Strip None values — NewsAPI treats empty strings as invalid
        clean_params = {k: v for k, v in params.items() if v is not None}

        logger.debug("NewsAPI request: GET %s params=%s", url, clean_params)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=clean_params, headers=self._headers)
        except httpx.TimeoutException as exc:
            logger.error("NewsAPI timeout: %s", exc)
            raise HTTPException(status_code=504, detail="Upstream NewsAPI timed out.") from exc
        except httpx.RequestError as exc:
            logger.error("NewsAPI connection error: %s", exc)
            raise HTTPException(status_code=502, detail="Could not reach NewsAPI.") from exc

        data: dict[str, Any] = response.json()

        if data.get("status") == "error":
            code: str = data.get("code", "unexpectedError")
            message: str = data.get("message", "Unknown upstream error.")
            http_status = _NEWSAPI_ERROR_MAP.get(code, 502)
            logger.warning("NewsAPI error %s (%s): %s", http_status, code, message)
            raise HTTPException(status_code=http_status, detail={"code": code, "message": message})

        if response.status_code != 200:
            logger.error("Unexpected NewsAPI HTTP %d: %s", response.status_code, data)
            raise HTTPException(status_code=502, detail="Unexpected response from NewsAPI.")

        return data

    # ------------------------------------------------------------------
    # Public methods — one per endpoint group
    # ------------------------------------------------------------------

    async def get_top_headlines(
        self,
        *,
        country: str | None = None,
        category: str | None = None,
        sources: str | None = None,
        page_size: int = 20,
        page: int = 1,
    ) -> dict[str, Any]:
        """Fetch top headlines from NewsAPI /v2/top-headlines.

        Args:
            country: 2-letter country code. Ignored when sources is set.
            category: One of business, entertainment, general, health,
                      science, sports, technology. Ignored when sources is set.
            sources: Comma-separated source IDs.
            page_size: Number of results per page (1-100).
            page: Page number.

        Returns:
            Raw NewsAPI JSON dict with status, totalResults, articles.
        """
        params: dict[str, Any] = {
            "pageSize": page_size,
            "page": page,
        }
        if sources:
            params["sources"] = sources
        else:
            params["country"] = country
            params["category"] = category

        return await self._get("/top-headlines", params)

    async def search_articles(
        self,
        *,
        q: str,
        from_date: str | None = None,
        to_date: str | None = None,
        language: str | None = None,
        sort_by: str = "publishedAt",
        page_size: int = 20,
        page: int = 1,
    ) -> dict[str, Any]:
        """Full-text article search via NewsAPI /v2/everything.

        Args:
            q: Search keywords or phrase.
            from_date: Oldest article date (ISO 8601, YYYY-MM-DD).
            to_date: Newest article date (ISO 8601, YYYY-MM-DD).
            language: ISO-639-1 language code.
            sort_by: relevancy | popularity | publishedAt.
            page_size: Number of results per page (1-100).
            page: Page number.

        Returns:
            Raw NewsAPI JSON dict with status, totalResults, articles.
        """
        params: dict[str, Any] = {
            "q": q,
            "from": from_date,
            "to": to_date,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page,
        }
        return await self._get("/everything", params)

    async def get_trending(
        self,
        *,
        language: str = "en",
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Fetch trending news by retrieving the most popular recent articles.

        Uses NewsAPI /v2/top-headlines with a broad query, sorted by
        popularity, to surface what is currently trending globally.

        Args:
            language: ISO-639-1 language code.
            page_size: Number of results (1-100).

        Returns:
            Raw NewsAPI JSON dict with status, totalResults, articles.
        """
        # top-headlines doesn't support language filtering or sortBy, so we
        # use /everything with a wildcard-style broad query and popularity sort.
        params: dict[str, Any] = {
            "q": "news",
            "language": language,
            "sortBy": "popularity",
            "pageSize": page_size,
            "page": 1,
        }
        return await self._get("/everything", params)

    async def get_sources(
        self,
        *,
        category: str | None = None,
        language: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve available news sources from NewsAPI /v2/top-headlines/sources.

        Args:
            category: Filter by category.
            language: Filter by ISO-639-1 language code.
            country: Filter by ISO 3166-1 country code.

        Returns:
            Raw NewsAPI JSON dict with status and sources list.
        """
        params: dict[str, Any] = {
            "category": category,
            "language": language,
            "country": country,
        }
        return await self._get("/top-headlines/sources", params)
