from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def sample_payload():
    return {
        "race": "Caucasian", "gender": "Female", "age": "[50-60)",
        "admission_type_id": 1, "discharge_disposition_id": 1, "admission_source_id": 7,
        "time_in_hospital": 3, "payer_code": "MC", "medical_specialty": "InternalMedicine",
        "num_lab_procedures": 40, "num_procedures": 0, "num_medications": 12,
        "number_outpatient": 0, "number_emergency": 0, "number_inpatient": 0,
        "diag_1": "250.83", "diag_2": "276", "diag_3": "414",
        "number_diagnoses": 7, "max_glu_serum": "None", "A1Cresult": "None",
        "metformin": "No", "repaglinide": "No", "nateglinide": "No",
        "chlorpropamide": "No", "glimepiride": "No", "acetohexamide": "No",
        "glipizide": "No", "glyburide": "No", "tolbutamide": "No",
        "pioglitazone": "No", "rosiglitazone": "No", "acarbose": "No",
        "miglitol": "No", "troglitazone": "No", "tolazamide": "No",
        "examide": "No", "citoglipton": "No", "insulin": "No",
        "glyburide-metformin": "No", "glipizide-metformin": "No",
        "glimepiride-pioglitazone": "No", "metformin-rosiglitazone": "No",
        "metformin-pioglitazone": "No", "change": "No", "diabetesMed": "No",
    }


def test_valid_prediction_and_response_structure():
    response = client.post("/api/predict", json=sample_payload())
    assert response.status_code == 200, response.text
    body = response.json()
    assert set(body) == {
        "predicted_class", "predicted_outcome", "probability_lt30",
        "probability_gt30", "probability_no",
    }
    assert body["predicted_class"] in {"<30", ">30", "NO"}
    assert body["predicted_outcome"] in {
        "Readmitted within 30 days", "Readmitted after 30 days", "Not readmitted",
    }
    probs = [body["probability_lt30"], body["probability_gt30"], body["probability_no"]]
    assert all(0.0 <= value <= 1.0 for value in probs)
    assert abs(sum(probs) - 1.0) < 1e-6
