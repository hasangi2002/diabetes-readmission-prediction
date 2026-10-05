from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


# Finite categories observed in the source dataset. The encoder safely handles
# future categories, but the API rejects typos for these defined vocabularies.
PAYER_CODES = {"BC", "CH", "CM", "CP", "DM", "FR", "HM", "MC", "MD", "MP", "OG", "OT", "PO", "SI", "SP", "UN", "WC", "?"}
MEDICAL_SPECIALTIES = {
    "AllergyandImmunology", "Anesthesiology", "Anesthesiology-Pediatric", "Cardiology", "Cardiology-Pediatric", "DCPTEAM", "Dentistry", "Dermatology", "Emergency/Trauma", "Endocrinology", "Endocrinology-Metabolism", "Family/GeneralPractice", "Gastroenterology", "Gynecology", "Hematology", "Hematology/Oncology", "Hospitalist", "InfectiousDiseases", "InternalMedicine", "Nephrology", "Neurology", "Neurophysiology", "Obsterics&Gynecology-GynecologicOnco", "Obstetrics", "ObstetricsandGynecology", "Oncology", "Ophthalmology", "Orthopedics", "Orthopedics-Reconstructive", "Osteopath", "Otolaryngology", "OutreachServices", "Pathology", "Pediatrics", "Pediatrics-AllergyandImmunology", "Pediatrics-CriticalCare", "Pediatrics-EmergencyMedicine", "Pediatrics-Endocrinology", "Pediatrics-Hematology-Oncology", "Pediatrics-InfectiousDiseases", "Pediatrics-Neurology", "Pediatrics-Pulmonology", "Perinatology", "PhysicalMedicineandRehabilitation", "PhysicianNotFound", "Podiatry", "Proctology", "Psychiatry", "Psychiatry-Addictive", "Psychiatry-Child/Adolescent", "Psychology", "Pulmonology", "Radiologist", "Radiology", "Resident", "Rheumatology", "Speech", "SportsMedicine", "Surgeon", "Surgery-Cardiovascular", "Surgery-Cardiovascular/Thoracic", "Surgery-Colon&Rectal", "Surgery-General", "Surgery-Maxillofacial", "Surgery-Neuro", "Surgery-Pediatric", "Surgery-Plastic", "Surgery-PlasticwithinHeadandNeck", "Surgery-Thoracic", "Surgery-Vascular", "SurgicalSpecialty", "Urology", "?"
}

# Numeric values and constrained categories are taken from the UCI source dataset.
# Diagnosis and specialty codes are intentionally strings: their vocabularies are broad.
class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    race: Literal["Caucasian", "AfricanAmerican", "Other", "Asian", "Hispanic", "?"]
    gender: Literal["Female", "Male", "Unknown/Invalid", "?"]
    age: Literal["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]
    admission_type_id: int = Field(ge=1, le=8)
    discharge_disposition_id: int = Field(ge=1, le=28)
    admission_source_id: int = Field(ge=1, le=25)
    time_in_hospital: int = Field(ge=1, le=14)
    payer_code: str = Field(min_length=1, max_length=2)
    medical_specialty: str = Field(min_length=1, max_length=50)
    num_lab_procedures: int = Field(ge=0, le=132)
    num_procedures: int = Field(ge=0, le=6)
    num_medications: int = Field(ge=0, le=81)
    number_outpatient: int = Field(ge=0, le=42)
    number_emergency: int = Field(ge=0, le=76)
    number_inpatient: int = Field(ge=0, le=21)
    diag_1: str = Field(min_length=1, max_length=10)
    diag_2: str = Field(min_length=1, max_length=10)
    diag_3: str = Field(min_length=1, max_length=10)
    number_diagnoses: int = Field(ge=1, le=16)
    max_glu_serum: Literal["None", ">300", "Norm", ">200", "?"]
    A1Cresult: Literal["None", ">7", ">8", "Norm", "?"]
    metformin: Literal["No", "Steady", "Up", "Down", "?"]
    repaglinide: Literal["No", "Steady", "Up", "Down", "?"]
    nateglinide: Literal["No", "Steady", "Up", "Down", "?"]
    chlorpropamide: Literal["No", "Steady", "Up", "Down", "?"]
    glimepiride: Literal["No", "Steady", "Up", "Down", "?"]
    acetohexamide: Literal["No", "Steady", "?"]
    glipizide: Literal["No", "Steady", "Up", "Down", "?"]
    glyburide: Literal["No", "Steady", "Up", "Down", "?"]
    tolbutamide: Literal["No", "Steady", "?"]
    pioglitazone: Literal["No", "Steady", "Up", "Down", "?"]
    rosiglitazone: Literal["No", "Steady", "Up", "Down", "?"]
    acarbose: Literal["No", "Steady", "Up", "Down", "?"]
    miglitol: Literal["No", "Steady", "Up", "Down", "?"]
    troglitazone: Literal["No", "Steady", "?"]
    tolazamide: Literal["No", "Steady", "Up", "?"]
    examide: Literal["No", "?"]
    citoglipton: Literal["No", "?"]
    insulin: Literal["No", "Steady", "Up", "Down", "?"]
    glyburide_metformin: Literal["No", "Steady", "Up", "Down", "?"] = Field(alias="glyburide-metformin")
    glipizide_metformin: Literal["No", "Steady", "?"] = Field(alias="glipizide-metformin")
    glimepiride_pioglitazone: Literal["No", "Steady", "?"] = Field(alias="glimepiride-pioglitazone")
    metformin_rosiglitazone: Literal["No", "Steady", "?"] = Field(alias="metformin-rosiglitazone")
    metformin_pioglitazone: Literal["No", "Steady", "?"] = Field(alias="metformin-pioglitazone")
    change: Literal["No", "Ch", "?"]
    diabetesMed: Literal["No", "Yes", "?"]

    @field_validator("payer_code")
    @classmethod
    def known_payer_code(cls, value: str) -> str:
        if value not in PAYER_CODES:
            raise ValueError("must be a payer code observed in the source dataset (or ? for missing)")
        return value

    @field_validator("medical_specialty")
    @classmethod
    def known_specialty(cls, value: str) -> str:
        if value not in MEDICAL_SPECIALTIES:
            raise ValueError("must be a medical specialty observed in the source dataset (or ? for missing)")
        return value

    @field_validator("diag_1", "diag_2", "diag_3")
    @classmethod
    def valid_diagnosis_code(cls, value: str) -> str:
        # The source data includes numeric diagnosis values shorter than three
        # digits as well as standard 3-digit and decimal ICD-9 forms.
        if value != "?" and not re.fullmatch(r"(?:[VE][0-9]{2,3}(?:\.[0-9]{1,2})?|[0-9]{1,3}(?:\.[0-9]{1,2})?)", value):
            raise ValueError("must be an ICD-9 diagnosis code or ? for missing")
        return value

    @field_validator("payer_code", "medical_specialty", "diag_1", "diag_2", "diag_3")
    @classmethod
    def non_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must contain a non-whitespace value")
        return value
