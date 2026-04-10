# ChargeFlow Architecture

```mermaid
flowchart LR
    A["Public APIs<br/>NREL / Open-Meteo / EIA"] --> B["Day 1 Ingestion"]
    B --> C["Raw Layer<br/>JSON files"]
    C --> D["Day 2 Synthetic Generation"]
    D --> E["Processed Layer<br/>CSV operational data"]
    C --> F["Day 3 Warehouse Loader"]
    E --> F
    F --> G["SQLite Warehouse<br/>stage / dim / fact / gold"]
    G --> H["Day 4 ML Pipelines"]
    H --> I["Model Artifacts<br/>predictions / metrics"]
    G --> J["Day 5 Recommendation Service"]
    E --> K["Day 5 Retrieval Index"]
    I --> J
    K --> L["FastAPI"]
    J --> L
    I --> M["Day 6 Streamlit App"]
    G --> M
    L --> N["Hosted Demo on Vercel"]
    M --> O["Local Companion App"]
    G --> P["Power BI Export Bundle"]
```

## Explanation

- Day 1 ingests public EV, weather, and energy data into a raw landing zone.
- Day 2 generates synthetic operational data anchored to the real station layer.
- Day 3 loads raw and synthetic data into a local SQL warehouse and produces gold marts.
- Day 4 trains baseline models and saves prediction artifacts.
- Day 5 adds recommendation scoring and retrieval over maintenance knowledge, exposed via FastAPI.
- Day 6 surfaces the system through a local Streamlit companion app, a hosted Vercel demo, and Power BI-ready exports.
