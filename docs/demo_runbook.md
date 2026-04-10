# Demo Runbook

## Local Demo Flow

1. Refresh the recommendation snapshot and RAG index:

```bash
python3 -m src.rag.cli build-index
```

2. Run the API if you want live local service endpoints:

```bash
python3 -m uvicorn api.main:app --reload
```

3. Run the local Streamlit companion app:

```bash
python3 -m streamlit run app/streamlit_app.py
```

4. Export the Power BI bundle:

```bash
python3 scripts/export_powerbi.py
```

## Hosted Demo Flow

1. Open the Vercel frontend
2. Show the project overview and recommendations
3. Run an operations question in the retrieval assistant
4. Explain that the hosted demo uses checked-in portfolio assets while the local app shows the full project pipeline

## Good Questions To Demo

- `How should I respond to a cooling alarm?`
- `Show me the best station recommendations in California`
- `What does the failure-risk model predict?`
