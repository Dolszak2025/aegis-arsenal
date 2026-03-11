"""Tests for Aegis Arsenal FastAPI application"""

import pytest
from starlette.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestMainPage:
    """Tests for the main page endpoint"""

    def test_read_root_status_code(self, client):
        """Test that GET / returns 200 OK"""
        response = client.get("/")
        assert response.status_code == 200

    def test_read_root_content_type(self, client):
        """Test that main page returns HTML"""
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_read_root_contains_title(self, client):
        """Test that main page contains Aegis Arsenal title"""
        response = client.get("/")
        assert "Aegis Arsenal" in response.text

    def test_read_root_contains_speed_insights(self, client):
        """Test that Speed Insights script is included"""
        response = client.get("/")
        assert "window.si = window.si || function" in response.text
        assert "_vercel/speed-insights/script.js" in response.text

    def test_read_root_contains_features(self, client):
        """Test that features are displayed on main page"""
        response = client.get("/")
        assert "Fast API Backend" in response.text
        assert "Vercel Speed Insights" in response.text
        assert "Production Ready" in response.text

    def test_read_root_valid_html(self, client):
        """Test that main page returns valid HTML structure"""
        response = client.get("/")
        assert "<!DOCTYPE html>" in response.text
        assert "<html" in response.text
        assert "</html>" in response.text
        assert "<head>" in response.text
        assert "<body>" in response.text


class TestHealthEndpoint:
    """Tests for the health check endpoint"""

    def test_health_check_status_code(self, client):
        """Test that health check returns 200 OK"""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_content_type(self, client):
        """Test that health check returns JSON"""
        response = client.get("/api/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_check_response_body(self, client):
        """Test health check response structure"""
        response = client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert "message" in data
        assert data["status"] == "healthy"

    def test_health_check_message_contains_app_name(self, client):
        """Test that health check message includes app name"""
        response = client.get("/api/health")
        data = response.json()
        assert "Aegis Arsenal" in data["message"]


class TestInfoEndpoint:
    """Tests for the application info endpoint"""

    def test_info_status_code(self, client):
        """Test that info endpoint returns 200 OK"""
        response = client.get("/api/info")
        assert response.status_code == 200

    def test_info_content_type(self, client):
        """Test that info endpoint returns JSON"""
        response = client.get("/api/info")
        assert response.headers["content-type"] == "application/json"

    def test_info_response_structure(self, client):
        """Test info response structure"""
        response = client.get("/api/info")
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "framework" in data
        assert "features" in data

    def test_info_app_name(self, client):
        """Test that info contains correct app name"""
        response = client.get("/api/info")
        data = response.json()
        assert data["name"] == "Aegis Arsenal"

    def test_info_version_format(self, client):
        """Test that version follows semantic versioning"""
        response = client.get("/api/info")
        data = response.json()
        version = data["version"]

        # Check semantic versioning format X.Y.Z
        parts = version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_info_framework(self, client):
        """Test that framework is correctly identified"""
        response = client.get("/api/info")
        data = response.json()
        assert data["framework"] == "FastAPI"

    def test_info_features(self, client):
        """Test that features list is correct"""
        response = client.get("/api/info")
        data = response.json()
        features = data["features"]

        assert isinstance(features, list)
        assert "Vercel Speed Insights" in features
        assert "RESTful API" in features


class TestAppMetadata:
    """Tests for application metadata"""

    def test_app_title(self):
        """Test that FastAPI app has correct title"""
        assert app.title == "Aegis Arsenal"

    def test_app_has_routes(self):
        """Test that app has defined routes"""
        routes = [route.path for route in app.routes]
        assert "/" in routes
        assert "/api/health" in routes
        assert "/api/info" in routes

    def test_app_minimum_route_count(self):
        """Test that app has at least 3 routes"""
        # Including automatic OpenAPI routes
        assert len(app.routes) >= 3


class TestHttpMethods:
    """Tests for HTTP method handling"""

    def test_root_get_only(self, client):
        """Test that root only accepts GET"""
        assert client.get("/").status_code == 200
        assert client.post("/").status_code == 405
        assert client.put("/").status_code == 405
        assert client.delete("/").status_code == 405

    def test_health_get_only(self, client):
        """Test that health endpoint only accepts GET"""
        assert client.get("/api/health").status_code == 200
        assert client.post("/api/health").status_code == 405

    def test_info_get_only(self, client):
        """Test that info endpoint only accepts GET"""
        assert client.get("/api/info").status_code == 200
        assert client.post("/api/info").status_code == 405


class TestErrorHandling:
    """Tests for error handling"""

    def test_nonexistent_route(self, client):
        """Test that nonexistent route returns 404"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_json_path(self, client):
        """Test behavior with invalid paths"""
        response = client.get("/api/invalid")
        assert response.status_code == 404


class TestPerformance:
    """Tests for response performance"""

    def test_root_response_time(self, client):
        """Test that root endpoint responds quickly"""
        import time

        start = time.time()
        response = client.get("/")
        duration = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert duration < 1000  # Should respond within 1 second

    def test_health_response_time(self, client):
        """Test that health check responds very quickly"""
        import time

        start = time.time()
        response = client.get("/api/health")
        duration = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert duration < 100  # Health check should be < 100ms


class TestResponseValidation:
    """Tests for response validation"""

    def test_health_check_json_valid(self, client):
        """Test that health check returns valid JSON"""
        response = client.get("/api/health")
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("Health check did not return valid JSON")

    def test_info_json_valid(self, client):
        """Test that info returns valid JSON"""
        response = client.get("/api/info")
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("Info endpoint did not return valid JSON")
