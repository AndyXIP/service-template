# service-template

![Status](https://img.shields.io/badge/Status-Template-blue) ![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688?logo=fastapi&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-2-E92063?logo=pydantic&logoColor=white) ![structlog](https://img.shields.io/badge/structlog-JSON%20logging-black) ![License](https://img.shields.io/badge/License-MIT-green)

A FastAPI backend service template. Clone it, delete the example `items`
resource, and build your actual service in its place — the surrounding
structure (config, structured logging, error handling, layered architecture,
tests, CI, Docker) is meant to be copied as-is.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development Notes](#development-notes)
- [Suggested Future Directions](#suggested-future-directions)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

This is a starting point for a new backend service, not a finished product.
The `items` resource in `src/` is a worked example — full CRUD, layered
architecture, validation, error handling, and tests — that exists purely to
demonstrate the patterns a new resource in your real service should follow.
Everything around it (Docker, CI, pre-commit, task runner) is already
production-flavored and untouched by the example.

---

## Features

- **Layered architecture** — domain entities, API schemas, repositories, and
  services are cleanly separated; routes stay thin controllers.
- **Typed configuration** — `pydantic-settings` reads env vars / `.env`,
  validated at startup.
- **Structured JSON logging** — `structlog`, with uvicorn's own logs routed
  through the same formatter and one log line per request (method, path,
  status, duration). Health-check polling is excluded from request logs.
- **Consistent error handling** — validation errors, domain "not found"
  errors, and unhandled exceptions all resolve to the same JSON envelope
  shape, with no internals leaked on 500s.
- **Stubbed auth wiring** — a `Depends`-based bearer-token dependency
  (`src/core/auth.py`) shows how to require authentication on a route and
  get a 401 envelope on failure. It does not verify tokens — see
  [Development Notes](#development-notes).
- **Full example CRUD resource** — `items`, with proper HTTP status codes
  (201/200/204/404/422) to copy from.
- **Real test suite** — unit tests per layer plus integration tests through
  the full HTTP stack.
- **Production-flavored Docker/CI** — multi-stage build, non-root user,
  `HEALTHCHECK`, and a GitHub Actions pipeline that lints, type-checks,
  tests, and smoke-tests the built image.

---

## Architecture

```
┌───────────────────────────┐
│  Client                   │
└────────────┬──────────────┘
             │  HTTP
             ▼
┌───────────────────────────┐
│  api/routes                │  thin controllers: parse schema, call service
├───────────────────────────┤
│  services                  │  business logic, orchestrates repositories
├───────────────────────────┤
│  repositories               │  storage abstraction (in-memory for this template)
├───────────────────────────┤
│  domain                      │  entities + domain exceptions, framework-agnostic
└───────────────────────────┘
             ▲
             │  DTOs at the boundary only
      schemas (pydantic request/response models)
```

`core/` (`config`, `logging`, `errors`, `auth`) is cross-cutting
infrastructure used by every layer above, not part of the request-flow
chain itself.

---

## Tech Stack

- **FastAPI** — async web framework with automatic OpenAPI docs
- **Uvicorn** — ASGI server
- **Pydantic v2 / pydantic-settings** — validation and typed settings
- **structlog** — structured JSON logging
- **uv** — Python package manager
- **mise** — dev tool + task runner (Python, uv, lint/test/build tasks)
- **Ruff** — linter and formatter
- **ty** — type checker
- **pytest** — test runner

---

## Project Structure

```
service-template/
├── .github/workflows/       # CI: lint+typecheck, test, build+smoke test
├── src/
│   ├── main.py                # app factory + lifespan
│   ├── core/
│   │   ├── config.py            # pydantic-settings Settings
│   │   ├── logging.py            # structlog config + request-logging middleware
│   │   ├── errors.py              # exception handlers, JSON error envelope
│   │   └── auth.py                 # stubbed bearer-token auth dependency
│   ├── domain/                     # entities + domain exceptions (framework-agnostic)
│   ├── schemas/                      # pydantic request/response DTOs (API boundary)
│   ├── repositories/                   # storage abstraction (in-memory here)
│   ├── services/                         # business logic, orchestrates repositories
│   └── api/routes/                         # FastAPI routers
├── tests/
│   ├── unit/                # fast, isolated per-layer tests
│   └── integration/          # full HTTP stack via TestClient
├── .env.example              # documents Settings fields
├── Dockerfile                 # multi-stage, non-root, HEALTHCHECK
├── .pre-commit-config.yaml
├── pyproject.toml
└── uv.lock
```

---

## Getting Started

**Prerequisite:** [mise](https://mise.jdx.dev/)

```bash
brew install mise
```

`cd` into the repo — mise's `enter` hook auto-runs `uv sync` and installs the
pre-commit hooks. Then:

```bash
mise run dev
```

The API is available at `http://127.0.0.1:8000`:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/utils/health`

---

## Configuration

All configuration is loaded from environment variables via `pydantic-settings`
(`src/core/config.py`). See `.env.example` for a ready-to-copy template — all
fields have defaults, so `.env` is optional.

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `service-template` | Used in the OpenAPI title and startup log |
| `ENVIRONMENT` | `local` | One of `local`, `staging`, `production` |
| `LOG_LEVEL` | `INFO` | Standard Python log level name |
| `CORS_ORIGINS` | `[]` | JSON list of allowed origins; CORS middleware is only added if non-empty |
| `DEBUG` | `false` | Reserved for local debugging toggles |

---

## Usage

| Method | Path | Description |
|---|---|---|
| `GET` | `/utils/health` | Liveness check (used by Docker `HEALTHCHECK` and CI) |
| `POST` | `/items` | Create an item (requires bearer token) — 201 |
| `GET` | `/items` | List items |
| `GET` | `/items/{id}` | Get one item — 404 if missing |
| `PATCH` | `/items/{id}` | Partially update an item (requires bearer token) — 404 if missing |
| `DELETE` | `/items/{id}` | Delete an item (requires bearer token) — 204 |

```bash
curl -X POST localhost:8000/items \
  -H 'content-type: application/json' \
  -H 'authorization: Bearer test-token' \
  -d '{"name": "Widget", "description": "A widget", "price": 9.99}'

curl localhost:8000/items
curl localhost:8000/items/<id>
curl -X PATCH localhost:8000/items/<id> -H 'authorization: Bearer test-token' -d '{"price": 14.99}'
curl -X DELETE localhost:8000/items/<id> -H 'authorization: Bearer test-token'
```

---

## Development Notes

- **In-memory only**: the `items` store lives in `app.state`, reset on every
  restart (and fresh per test) — no database is wired up on purpose, so the
  template stays unopinionated about which one you'll use.
- **Swap the repository, not the API**: `InMemoryItemRepository`
  (`src/repositories/item.py`) implements the `ItemRepository` protocol.
  Replace it with a real implementation and nothing above the repository
  layer needs to change.
- **Error envelope**: every error response — validation, not-found, auth, or
  unhandled — has the shape `{"error": {"type", "message", "details"}}`.
- **Auth is a stub, not real security**: `get_current_principal`
  (`src/core/auth.py`) only checks that a bearer token is present - it does
  not verify a signature, expiry, or issuer, and accepts any non-empty
  token. It exists to show the wiring pattern (`Depends(get_current_principal)`
  on a route, a 401 envelope on failure) so every service doesn't reinvent
  it independently. Replace `_authenticate` with real verification (JWT
  signature/expiry check, an introspection call to your identity provider,
  etc.) before relying on it. The example `items` writes (`POST`/`PATCH`/
  `DELETE`) require it; reads don't - adjust the split to your service's needs.
- **CI pipeline**: pushes and PRs run `mise run check` (lint + typecheck),
  `mise run test`, and `mise run build` (Docker build + health-check smoke
  test) via GitHub Actions.

```bash
mise run test        # full suite (tests/unit + tests/integration)
mise run test-unit   # fast unit-only subset
mise run check        # ruff + ty
```

---

## Suggested Future Directions

Things intentionally left out of the template — add them once your service
actually needs them:

- A real persistence layer (swap `InMemoryItemRepository` for a SQL/Mongo-backed one)
- Real auth: replace the stub in `src/core/auth.py` with actual token
  verification (JWT signature/expiry check, an identity provider
  integration, etc.) and, if needed, authorization (roles/scopes)
- Pagination on list endpoints
- Rate limiting
- Metrics/tracing
- A readiness endpoint (only meaningful once there's a real dependency, like a DB, to check)
- `deploy.yml` — currently a stub

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — web framework
- [Pydantic](https://docs.pydantic.dev/) — validation and settings
- [structlog](https://www.structlog.org/) — structured logging
- [uv](https://docs.astral.sh/uv/) — package manager
- [mise](https://mise.jdx.dev/) — dev tool and task runner
- [Ruff](https://docs.astral.sh/ruff/) — linter and formatter
