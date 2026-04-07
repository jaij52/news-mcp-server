# CLAUDE.md — News MCP Server

## Project Identity
- **Name**: news-mcp-server
- **Purpose**: MCP server exposing news search tools via FastAPI
- **Language**: Python 3.11+
- **Framework**: FastAPI + fastapi-mcp

## Coding Standards
- Use `async def` for all route handlers and service methods
- Type hints on ALL function signatures (params + return types)
- Pydantic models for all request params and response shapes
- Use `httpx.AsyncClient` for external HTTP calls (not requests)
- Environment variables via pydantic-settings, never hardcoded secrets
- Docstrings on every public function (these become MCP tool descriptions)

## Architecture Rules
- Routes go in `src/news_mcp/routes/` — one file per endpoint group
- Business logic goes in `src/news_mcp/services/` — routes stay thin
- Pydantic models go in `src/news_mcp/models/schemas.py`
- Config/settings go in `src/news_mcp/config.py`
- No global mutable state; use dependency injection via FastAPI `Depends()`

## MCP Integration
- Use `fastapi-mcp` to auto-expose all FastAPI routes as MCP tools
- Every route MUST have a clear `summary` and `description` in the decorator
- Every route MUST have a meaningful `operation_id` (this becomes the MCP tool name)
- Example: `@router.get("/api/headlines", operation_id="get_top_headlines", summary="Get top news headlines")`

## Error Handling
- Wrap all external API calls in try/except
- Return structured error responses, never raw exceptions
- Use FastAPI's HTTPException for client errors
- Log errors to stdout (structured logging preferred)

## Testing
- Use pytest + httpx.AsyncClient for async route tests
- Mock the NewsAPI.org responses — never call the real API in tests
- Test both success and error cases

## What NOT to do
- Do NOT hardcode the NewsAPI key anywhere
- Do NOT use `requests` library (use `httpx` for async)
- Do NOT put business logic in route handlers
- Do NOT use print() for logging — use Python's logging module