from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.model_loader import ModelLoadError
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


def test_unknown_admission_code_returns_422():
    payload = sample_payload()
    payload["admission_source_id"] = 12
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
    assert "admission_source_id" in response.text


def test_excluded_hospice_discharge_returns_422():
    payload = sample_payload()
    payload["discharge_disposition_id"] = 13
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
    assert "death and hospice" in response.text


def test_malformed_json_returns_422():
    response = client.post(
        "/api/predict",
        content="{not valid json",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 422


def test_model_unavailable_returns_sanitized_503(monkeypatch):
    def unavailable():
        raise ModelLoadError("private artifact path and deserialization details")

    monkeypatch.setattr("backend.app.main.load_model_bundle", unavailable)
    response = client.get("/api/model-info")
    assert response.status_code == 503
    assert response.json() == {"detail": "Prediction model is currently unavailable"}
    assert "private artifact path" not in response.text


def test_prediction_failure_returns_sanitized_error(monkeypatch):
    def failed_prediction(_request):
        raise RuntimeError("private traceback detail")

    monkeypatch.setattr("backend.app.main.predict", failed_prediction)
    response = client.post("/api/predict", json=sample_payload())
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Prediction could not be generated for this input"
    }
    assert "private traceback detail" not in response.text
    assert "Traceback" not in response.text
