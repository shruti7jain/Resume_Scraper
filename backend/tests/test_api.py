from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_analyze_endpoint():
    # Valid payload but we'd need valid objects. 
    # Just checking 422 for bad payload first
    response = client.post("/api/analyze", json={})
    assert response.status_code == 422

def test_optimize_endpoint():
    response = client.post("/api/optimize", json={})
    assert response.status_code == 422

def test_download_pdf_endpoint():
    response = client.post("/api/download-pdf", json={})
    assert response.status_code == 422
