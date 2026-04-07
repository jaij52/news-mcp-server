"""Route handler for /api/trending."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from news_mcp.config import Settings, get_settings
from news_mcp.models.schemas import ArticlesResponse
from news_mcp.services.news_service import NewsService

logger = logging.getLogger(__name__)

router = APIRouter()


def _news_service(settings: Annotated[Settings, Depends(get_settings)]) -> NewsService:
    return NewsService(settings)


@router.get(
    "/api/trending",
    operation_id="get_trending_news",
    summary="Get currently trending news stories",
    description=(
        "Retrieve the most popular and widely-read news stories right now. "
        "Uses NewsAPI's popularity sort across all sources to surface what the world is reading. "
        "Filter by language. Returns a concise list of top trending articles."
    ),
    response_model=ArticlesResponse,
)
async def get_trending_news(
    service: Annotated[NewsService, Depends(_news_service)],
    language: Annotated[
        str,
        Query(description="ISO-639-1 language code for trending stories, e.g. 'en', 'es'."),
    ] = "en",
    page_size: Annotated[
        int,
        Query(ge=1, le=100, alias="pageSize", description="Number of trending articles to return (1-100)."),
    ] = 10,
) -> ArticlesResponse:
    """Return the most-read/trending articles across all sources for a given language."""
    logger.info("get_trending_news language=%s page_size=%d", language, page_size)
    data = await service.get_trending(language=language, page_size=page_size)
    return ArticlesResponse(**data)
