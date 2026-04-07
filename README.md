# news-mcp-server

A FastAPI-based MCP server that exposes [NewsAPI.org](https://newsapi.org) as structured tools via [fastapi-mcp](https://github.com/tadata-org/fastapi-mcp).

## Endpoints / MCP Tools

| Route | Operation ID (MCP tool name) | Description |
|---|---|---|
| `GET /api/headlines` | `get_top_headlines` | Top headlines filtered by country, category, or source |
| `GET /api/search` | `search_news_articles` | Full-text article search with date range and sort options |
| `GET /api/trending` | `get_trending_news` | Most-read stories right now, filtered by language |
| `GET /api/sources` | `get_news_sources` | Browse available publishers by category, language, country |

## Setup

### 1. Get a NewsAPI key

Sign up at <https://newsapi.org/register> and copy your API key.

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set NEWS_API_KEY=your_key_here
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Run the server

```bash
uvicorn news_mcp.main:app --reload
# or
news-mcp
```

The server starts on `http://localhost:8000`.

- Swagger UI: `http://localhost:8000/docs`
- MCP endpoint: `http://localhost:8000/mcp` (auto-mounted by fastapi-mcp)

## Use with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "news": {
      "command": "uvicorn",
      "args": ["news_mcp.main:app", "--port", "8000"],
      "env": {
        "NEWS_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Running tests

```bash
pytest
```

Tests mock all NewsAPI HTTP calls — no real network traffic or API key required.

## Project structure

```
src/news_mcp/
├── main.py          # App factory, MCP mount
├── config.py        # pydantic-settings config
├── models/
│   └── schemas.py   # All Pydantic request/response models
├── services/
│   └── news_service.py  # NewsAPI HTTP logic
└── routes/
    ├── headlines.py
    ├── search.py
    ├── trending.py
    └── sources.py
tests/
├── conftest.py
├── test_headlines.py
├── test_search.py
├── test_trending.py
└── test_sources.py
```
