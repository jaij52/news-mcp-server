"""Application entry point — wires FastAPI app and mounts fastapi-mcp."""

import logging

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from news_mcp.config import configure_logging, get_settings
from news_mcp.routes import headlines, search, sources, trending

# Bootstrap logging before anything else
configure_logging(get_settings())

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Construct and return the configured FastAPI application.

    Registers all route groups and attaches the fastapi-mcp integration
    so every route is automatically exposed as an MCP tool.
    """
    settings = get_settings()

    app = FastAPI(
        title="News MCP Server",
        description=(
            "An MCP server that exposes NewsAPI.org as structured tools: "
            "top headlines, full-text search, trending stories, and source discovery."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register route groups
    app.include_router(headlines.router, tags=["Headlines"])
    app.include_router(search.router, tags=["Search"])
    app.include_router(trending.router, tags=["Trending"])
    app.include_router(sources.router, tags=["Sources"])

    # Mount MCP — auto-discovers all routes and exposes them as MCP tools
    mcp = FastApiMCP(app)
    mcp.mount_http()

    logger.info(
        "News MCP Server ready | env=%s log_level=%s",
        settings.app_env,
        settings.log_level,
    )

    return app


app = create_app()


def run() -> None:
    """CLI entry point: uvicorn news_mcp.main:app."""
    import uvicorn

    uvicorn.run("news_mcp.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
