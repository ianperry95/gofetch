# GoFetch

AI-powered RSS reader with smart ranking, clustering, and deduplication.

## Features

- **Smart Ranking** — Articles ranked by relevance to your interests using embeddings
- **Clustering** — Groups similar articles together to reduce noise
- **Deduplication** — Automatically detects duplicate or near-duplicate content
- **Miniflux Integration** — Uses Miniflux as the feed management backend
- **OPML Support** — Import and export your feed subscriptions
- **Dark Mode** — Full dark theme support
- **Keyboard Navigation** — Power-user friendly with vim-style shortcuts
- **Multiple Layouts** — Cards, list, or magazine view
- **Web UI Configuration** — Manage API keys and settings from the browser

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| Frontend | SvelteKit + Tailwind CSS v4 |
| Database | PostgreSQL with pgvector |
| Feeds | Miniflux |
| Embeddings | ONNX (local) or OpenAI |
| Deployment | Docker Compose |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- A Miniflux instance (included in the stack)

### Configuration

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Or configure via the web UI at `/settings` after starting.

### Running

```bash
docker compose up -d
```

The app will be available at `http://localhost:3001`.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOFETCH_DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://gofetch:changeme@localhost:5432/gofetch` |
| `GOFETCH_MINIFLUX_URL` | Miniflux base URL | `http://miniflux:8080` |
| `GOFETCH_MINIFLUX_API_KEY` | Miniflux API key | — |
| `GOFETCH_OPENAI_API_KEY` | OpenAI API key (for OpenAI embeddings) | — |
| `GOFETCH_EMBEDDING_PROVIDER` | `onnx` or `openai` | `onnx` |
| `GOFETCH_SECRET_KEY` | General secret key | — |

## Project Structure

```
gofetch/
├── api/                    # FastAPI backend
│   └── app/
│       ├── config.py       # Pydantic settings
│       ├── main.py         # App entrypoint & lifespan
│       ├── models/         # SQLAlchemy models
│       ├── routers/        # API route handlers
│       ├── services/       # Business logic
│       └── embeddings/     # Embedding providers
├── frontend/               # SvelteKit frontend
│   └── src/
│       ├── lib/
│       │   ├── api/        # API client & types
│       │   └── stores/     # Svelte stores
│       └── routes/         # Pages & layouts
├── scripts/
│   └── init-db.sql         # Database initialization
├── docker-compose.yml
└── Dockerfile
```

## License

AGPL-3.0
