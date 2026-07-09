ARG PYTHON_VERSION
ARG UV_VERSION

FROM python:${PYTHON_VERSION}-slim AS build
COPY --from=ghcr.io/astral-sh/uv:${UV_VERSION} /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:${PYTHON_VERSION}-slim AS final
RUN useradd --create-home app
WORKDIR /app

COPY --from=build /app/.venv ./.venv
COPY src/ ./src/

RUN chown -R app:app /app
USER app

EXPOSE 8000
ENV PATH="/app/.venv/bin:$PATH"

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/utils/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
