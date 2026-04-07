"""Route handler for /api/search."""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from news_mcp.config import Settings, get_settings
from news_mcp.models.schemas import ArticlesResponse
from news_mcp.services.news_service import NewsService

logger = logging.getLogger(__name__)

router = APIRouter()


def _news_service(settings: Annotated[Settings, Depends(get_settings)]) -> NewsService:
    return NewsService(settings)


@router.get(
    "/api/search",
    operation_id="search_news_articles",
    summary="Search news articles by keyword",
    description=(
        "Full-text search across millions of articles from NewsAPI.org's /v2/everything endpoint. "
        "Supports date range filtering, language selection, and sort order. "
        "Ideal for researching a topic, tracking a story over time, or finding coverage from specific periods."
    ),
    response_model=ArticlesResponse,
)
async def search_news_articles(
    service: Annotated[NewsService, Depends(_news_service)],
    q: Annotated[
        str,
        Query(description="Search keywords or phrase. Supports AND, OR, NOT, and quoted phrases."),
    ],
    from_date: Annotated[
        str | None,
        Query(alias="from", description="Oldest article date in ISO 8601 (YYYY-MM-DD)."),
    ] = None,
    to_date: Annotated[
        str | None,
        Query(alias="to", description="Newest article date in ISO 8601 (YYYY-MM-DD)."),
    ] = None,
    language: Annotated[
        str | None,
        Query(description="ISO-639-1 language code, e.g. 'en', 'de', 'fr'."),
    ] = None,
    sort_by: Annotated[
        Literal["relevancy", "popularity", "publishedAt"],
        Query(alias="sortBy", description="Sort order: relevancy, popularity, or publishedAt."),
    ] = "publishedAt",
    page_size: Annotated[
        int,
        Query(ge=1, le=100, alias="pageSize", description="Articles per page (1-100)."),
    ] = 20,
    page: Annotated[int, Query(ge=1, description="Page number.")] = 1,
) -> ArticlesResponse:
    """Search articles across all indexed sources using keywords and optional filters."""
    logger.info("search_news_articles q=%r language=%s sort_by=%s page=%d", q, language, sort_by, page)
    data = await service.search_articles(
        q=q,
        from_date=from_date,
        to_date=to_date,
        language=language,
        sort_by=sort_by,
        page_size=page_size,
        page=page,
    )
    return ArticlesResponse(**data)
