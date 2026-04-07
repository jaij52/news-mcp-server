"""Route handler for /api/headlines."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from news_mcp.config import Settings, get_settings
from news_mcp.models.schemas import ArticlesResponse, HeadlinesParams
from news_mcp.services.news_service import NewsService

logger = logging.getLogger(__name__)

router = APIRouter()


def _news_service(settings: Annotated[Settings, Depends(get_settings)]) -> NewsService:
    return NewsService(settings)


@router.get(
    "/api/headlines",
    operation_id="get_top_headlines",
    summary="Get top news headlines",
    description=(
        "Fetch the current top headlines from NewsAPI.org. "
        "Filter by country, category, or specific source IDs. "
        "Returns a paginated list of articles with title, description, URL, and publication metadata."
    ),
    response_model=ArticlesResponse,
)
async def get_top_headlines(
    service: Annotated[NewsService, Depends(_news_service)],
    country: Annotated[
        str,
        Query(description="2-letter ISO 3166-1 country code, e.g. 'us', 'gb', 'de'."),
    ] = "us",
    category: Annotated[
        str | None,
        Query(
            description="Category filter: business, entertainment, general, health, science, sports, technology."
        ),
    ] = None,
    sources: Annotated[
        str | None,
        Query(description="Comma-separated NewsAPI source IDs. Cannot be combined with country/category."),
    ] = None,
    page_size: Annotated[int, Query(ge=1, le=100, alias="pageSize", description="Articles per page.")] = 20,
    page: Annotated[int, Query(ge=1, description="Page number.")] = 1,
) -> ArticlesResponse:
    """Return top headlines optionally filtered by country, category, or source.

    When sources is provided, country and category are ignored (NewsAPI limitation).
    """
    logger.info(
        "get_top_headlines country=%s category=%s sources=%s page=%d",
        country, category, sources, page,
    )
    data = await service.get_top_headlines(
        country=country,
        category=category,
        sources=sources,
        page_size=page_size,
        page=page,
    )
    return ArticlesResponse(**data)
