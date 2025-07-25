"""
API Test Cases

Integration tests for the FastAPI endpoints.

Author: Adryan R A
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAPI:
    """Test cases for API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "services" in data
    
    def test_ask_endpoint_validation(self, client):
        """Test ask endpoint input validation."""
        # Test empty query
        response = client.post("/ask", json={"query": ""})
        assert response.status_code == 422
        
        # Test missing query
        response = client.post("/ask", json={})
        assert response.status_code == 422
    
    def test_reset_endpoint(self, client):
        """Test conversation reset endpoint."""
        response = client.post("/reset")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
