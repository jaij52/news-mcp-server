"""Pydantic models for all request parameters and response shapes."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class ArticleSource(BaseModel):
    """The publication that produced an article."""

    id: str | None = None
    name: str


class Article(BaseModel):
    """A single news article returned by NewsAPI."""

    source: ArticleSource
    author: str | None = None
    title: str
    description: str | None = None
    url: str
    url_to_image: str | None = Field(None, alias="urlToImage")
    published_at: datetime | None = Field(None, alias="publishedAt")
    content: str | None = None

    model_config = {"populate_by_name": True}


class NewsSource(BaseModel):
    """A news publisher registered with NewsAPI."""

    id: str
    name: str
    description: str
    url: str
    category: str
    language: str
    country: str


# ---------------------------------------------------------------------------
# Query parameter models
# ---------------------------------------------------------------------------


class HeadlinesParams(BaseModel):
    """Query parameters for /api/headlines."""

    country: str = Field(
        default="us",
        description="2-letter ISO 3166-1 country code (e.g. 'us', 'gb', 'de').",
    )
    category: str | None = Field(
        default=None,
        description=(
            "News category: business, entertainment, general, health, "
            "science, sports, or technology."
        ),
    )
    sources: str | None = Field(
        default=None,
        description="Comma-separated NewsAPI source IDs (cannot be used with country/category).",
    )
    page_size: int = Field(default=20, ge=1, le=100, description="Number of articles (1-100).")
    page: int = Field(default=1, ge=1, description="Page number for pagination.")


class SearchParams(BaseModel):
    """Query parameters for /api/search."""

    q: str = Field(description="Keywords or phrase to search for in article title and body.")
    from_date: str | None = Field(
        default=None,
        alias="from",
        description="Oldest article date in ISO 8601 format (YYYY-MM-DD).",
    )
    to_date: str | None = Field(
        default=None,
        alias="to",
        description="Newest article date in ISO 8601 format (YYYY-MM-DD).",
    )
    language: str | None = Field(
        default=None,
        description="2-letter ISO-639-1 language code (e.g. 'en', 'de', 'fr').",
    )
    sort_by: Literal["relevancy", "popularity", "publishedAt"] = Field(
        default="publishedAt",
        alias="sortBy",
        description="Sort order: relevancy, popularity, or publishedAt.",
    )
    page_size: int = Field(default=20, ge=1, le=100, description="Number of articles (1-100).")
    page: int = Field(default=1, ge=1, description="Page number for pagination.")

    model_config = {"populate_by_name": True}


class TrendingParams(BaseModel):
    """Query parameters for /api/trending."""

    language: str = Field(
        default="en",
        description="2-letter ISO-639-1 language code for trending topics.",
    )
    page_size: int = Field(default=10, ge=1, le=100, description="Number of articles (1-100).")


class SourcesParams(BaseModel):
    """Query parameters for /api/sources."""

    category: str | None = Field(
        default=None,
        description="Filter by category: business, entertainment, general, health, science, sports, technology.",
    )
    language: str | None = Field(
        default=None,
        description="Filter by 2-letter ISO-639-1 language code.",
    )
    country: str | None = Field(
        default=None,
        description="Filter by 2-letter ISO 3166-1 country code.",
    )


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ArticlesResponse(BaseModel):
    """Standard paginated articles response."""

    status: str
    total_results: int = Field(alias="totalResults")
    articles: list[Article]

    model_config = {"populate_by_name": True}


class SourcesResponse(BaseModel):
    """Response for /api/sources."""

    status: str
    sources: list[NewsSource]


class ErrorResponse(BaseModel):
    """Structured error body returned on failures."""

    status: str = "error"
    code: str
    message: str
