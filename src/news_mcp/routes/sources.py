"""Route handler for /api/sources."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from news_mcp.config import Settings, get_settings
from news_mcp.models.schemas import SourcesResponse
from news_mcp.services.news_service import NewsService

logger = logging.getLogger(__name__)

router = APIRouter()


def _news_service(settings: Annotated[Settings, Depends(get_settings)]) -> NewsService:
    return NewsService(settings)


@router.get(
    "/api/sources",
    operation_id="get_news_sources",
    summary="List available news sources",
    description=(
        "Retrieve all news publishers available through NewsAPI.org. "
        "Optionally filter by category, language, or country. "
        "Use source IDs returned here with the get_top_headlines tool's 'sources' parameter."
    ),
    response_model=SourcesResponse,
)
async def get_news_sources(
    service: Annotated[NewsService, Depends(_news_service)],
    category: Annotated[
        str | None,
        Query(
            description=(
                "Filter by category: business, entertainment, general, "
                "health, science, sports, technology."
            )
        ),
    ] = None,
    language: Annotated[
        str | None,
        Query(description="Filter by ISO-639-1 language code, e.g. 'en', 'de'."),
    ] = None,
    country: Annotated[
        str | None,
        Query(description="Filter by ISO 3166-1 country code, e.g. 'us', 'gb'."),
    ] = None,
) -> SourcesResponse:
    """Return a list of available news sources with their IDs, categories, and metadata."""
    logger.info("get_news_sources category=%s language=%s country=%s", category, language, country)
    data = await service.get_sources(category=category, language=language, country=country)
    return SourcesResponse(**data)
