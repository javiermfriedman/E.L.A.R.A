"""Unit tests for top-level `app.main` (health check & app wiring)."""

import pytest


@pytest.mark.unit
class TestHealthCheck:
    def test_health_returns_healthy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}


@pytest.mark.unit
class TestAppRouterRegistration:
    def test_all_expected_routers_are_registered(self):
        from app.main import app

        paths = {route.path for route in app.routes if hasattr(route, "path")}
        # A representative path from each router must be present.
        assert "/auth/" in paths
        assert "/auth/token" in paths
        assert "/agents/" in paths
        assert "/contacts/" in paths
        assert "/recordings/" in paths
        assert "/dialout" in paths
        assert "/call/status" in paths
        assert "/call/cancel" in paths
        assert "/health" in paths
