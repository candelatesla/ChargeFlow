# Vercel Deployment Guide

## Deployment Shape

- Hosted demo frontend: static Vercel site from `public/index.html`
- Hosted backend: FastAPI from `api/index.py`
- Local companion app: Streamlit, kept separate from the hosted demo

## Why This Works

- The hosted API reads from checked-in demo assets under `demo_assets/` if local generated artifacts are not present.
- Runtime-generated temporary files are written to `/tmp` on Vercel instead of the project directory.
- The RAG layer can answer without Groq. If `GROQ_API_KEY` is set, it can optionally generate richer grounded responses.

## Files Used By The Hosted Demo

- `demo_assets/synthetic/augmented_stations.csv`
- `demo_assets/synthetic/maintenance_notes.csv`
- `demo_assets/synthetic/maintenance_tickets.csv`
- `demo_assets/warehouse/gold_station_health.csv`
- `demo_assets/warehouse/gold_station_daily_metrics.csv`
- `demo_assets/ml/failure_risk_predictions.csv`
- `demo_assets/ml/exploratory_summary.json`

## Vercel Setup

1. Import the GitHub repository into Vercel.
2. Keep the default project root as the repository root.
3. Set the Python version from `.python-version`.
4. Add environment variables:
   - `GROQ_API_KEY` if you want LLM-backed grounded answers
5. Deploy.

## Hosted Endpoints

- `/`
- `/api/health`
- `/api/overview`
- `/api/recommendations`
- `/api/rag/query`

## Notes

- The hosted demo is intentionally read-oriented and portfolio-focused.
- Full retraining and raw ingestion remain local workflows and are not executed on every deploy.
