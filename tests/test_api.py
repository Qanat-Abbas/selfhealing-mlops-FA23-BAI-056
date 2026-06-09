import pytest
import requests

BASE_URL = "http://localhost:5000"


def test_health_endpoint():
    """GET /health must return HTTP 200 with status:healthy and model_version present."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    assert "model_version" in data


def test_predict_returns_label_and_confidence():
    """POST /predict must return label, confidence in [0,1], and model_version."""
    payload = {"text": "Spotlessly clean rooms with attentive staff and superb amenities throughout"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("label") in ["POSITIVE", "NEGATIVE"]
    assert 0 <= data.get("confidence") <= 1
    assert "model_version" in data


def test_predict_negative_text():
    """POST /predict with clearly negative text must return HTTP 200."""
    payload = {"text": "This is absolutely terrible and I hate it completely"}
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200


def test_health_returns_model_version_unstable():
    """GET /health must return model_version == 'unstable-v1' exactly."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("model_version") == "unstable-v1"
