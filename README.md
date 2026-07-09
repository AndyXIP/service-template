# service-template

A FastAPI backend service template. Clone it and replace the example `items`
resource with your own - the surrounding structure (config, logging, error
handling, tests, CI, Docker) is meant to be copied as-is.

## Project structure

```
src/
  main.py                 # app factory + lifespan
  core/
    config.py              # pydantic-settings Settings
    logging.py              # structlog config + request-logging middleware
    errors.py                # exception handlers, JSON error envelope
  domain/                    # framework-agnostic entities + domain exceptions
  schemas/                    # pydantic request/response DTOs (API boundary)
  repositories/                # storage abstraction (in-memory for this template)
  services/                     # business logic, orchestrates repositories
  api/routes/                    # thin FastAPI routers
```

Dependency direction: `api -> services -> repositories -> domain`. `schemas`
are used only at the API boundary to convert to/from `domain` entities, so the
two are free to diverge.

## Getting started

```
mise run dev
```

Then visit `http://localhost:8000/docs` for interactive API docs, or:

```
curl http://localhost:8000/utils/health
```

## Running tests

```
mise run test        # full suite (tests/unit + tests/integration)
mise run test-unit   # fast unit-only subset
```

## Lint & typecheck

```
mise run check
```

## Example: items API

```
curl -X POST localhost:8000/items \
  -H 'content-type: application/json' \
  -d '{"name": "Widget", "description": "A widget", "price": 9.99}'

curl localhost:8000/items
curl localhost:8000/items/<id>
curl -X PATCH localhost:8000/items/<id> -d '{"price": 14.99}'
curl -X DELETE localhost:8000/items/<id>
```

## Configuration

Settings are read from environment variables (and an optional `.env` file,
which is gitignored). See `.env.example` for the full list and defaults, and
`src/core/config.py` for the source of truth.

## What's intentionally not included

No database, no auth, no metrics/tracing. The `items` resource is backed by
an in-memory store purely to demonstrate the layering (route -> service ->
repository -> domain) without tying the template to a specific database.
Swap `InMemoryItemRepository` (`src/repositories/item.py`) for a real
implementation when you build on this.
