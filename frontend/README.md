# Diabetes Readmission Prediction frontend

React, Vite, Tailwind CSS, Axios, Recharts, and Lucide React interface for the project’s FastAPI prediction service.

## Run locally

Start the backend from the repository root:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Then start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`). The default API base URL is `http://127.0.0.1:8000`. To use another backend URL, copy `.env.example` to `.env.local`, set `VITE_API_URL`, and restart Vite.

The prediction page posts encounter details to `/api/predict`; the health and model status indicators use `/api/health` and `/api/model-info`. The model is loaded and applied by the backend. The frontend does not calculate or hard-code prediction results.

`src/data/insights.json` contains descriptive aggregates and the existing model’s feature-importance totals derived from the checked-in dataset and saved model. Model comparison values are read from `outputs/model_comparison.csv`.

This is an academic decision-support system, not a medical diagnosis tool.
