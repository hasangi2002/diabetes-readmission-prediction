from fastapi.testclient import TestClient

from backend.app.main import app
from backend.tests.test_prediction import sample_payload

client = TestClient(app)


def test_missing_required_input_returns_422():
    payload = sample_payload()
    del payload["age"]
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
    assert "age" in response.text


def test_invalid_numeric_input_returns_422():
    payload = sample_payload()
    payload["number_inpatient"] = -1
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
    assert "number_inpatient" in response.text


def test_invalid_category_returns_422():
    payload = sample_payload()
    payload["gender"] = "NotARealCategory"
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
    assert "gender" in response.text
