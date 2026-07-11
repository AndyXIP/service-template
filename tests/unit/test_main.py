import pytest
from fastapi.testclient import TestClient

from core.config import get_settings
from main import create_app


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """`get_settings` is lru_cached; env overrides below need a fresh read."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_lifespan_logs_startup_and_shutdown(capsys: pytest.CaptureFixture[str]) -> None:
    # configure_logging() points the root logger's handler at stderr, so
    # caplog (which relies on its own handler) never sees these records -
    # capsys, which reads the real stream, does.
    with TestClient(create_app()) as client:
        response = client.get("/utils/health")

    assert response.status_code == 200
    stderr = capsys.readouterr().err
    assert "starting_up" in stderr
    assert "shutting_down" in stderr


def test_cors_origins_configured_adds_cors_middleware(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["http://allowed.example.com"]')

    client = TestClient(create_app())
    response = client.get("/utils/health", headers={"Origin": "http://allowed.example.com"})

    assert response.headers["access-control-allow-origin"] == "http://allowed.example.com"


def test_no_cors_origins_by_default(client: TestClient) -> None:
    response = client.get("/utils/health", headers={"Origin": "http://not-configured.example.com"})

    assert "access-control-allow-origin" not in response.headers
