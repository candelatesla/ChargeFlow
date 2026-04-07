# Day 5 Recommendation and RAG Notes

## Scope

Day 5 adds a recommendation layer, a retrieval layer over maintenance knowledge, and FastAPI endpoints to expose both services.

## Recommendation Layer

- Inputs:
  - `gold_station_health.csv`
  - `gold_station_daily_metrics.csv`
  - `failure_risk_predictions.csv`
  - `augmented_stations.csv`
- Output:
  - `data/processed/recommender/station_recommendations_snapshot.csv`

The recommendation score combines:

- predicted failure risk
- historical reliability
- recent queue pressure
- recent station throughput

## RAG Layer

- Sources:
  - `maintenance_notes.csv`
  - `maintenance_tickets.csv`
  - local SOP markdown files under `docs/sops/`
- Retrieval:
  - TF-IDF vectorization with cosine similarity
- Outputs:
  - `data/processed/rag/rag_documents.csv`
  - `data/processed/rag/rag_index.joblib`
  - `data/processed/rag/rag_index_metadata.json`

If `GROQ_API_KEY` is available, the API can optionally produce a grounded LLM answer using the retrieved context. If not, it falls back to an extractive answer built from the retrieved snippets.

## API Endpoints

- `GET /health`
- `POST /recommendations`
- `POST /rag/query`

## Run

```bash
python3 -m src.rag.cli build-index
uvicorn api.main:app --reload
```
