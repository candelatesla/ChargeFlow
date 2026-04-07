from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.rag.service import answer_query, build_rag_index
from src.recommender.service import build_recommendation_snapshot, load_overview_summary, recommend_stations


app = FastAPI(title="ChargeFlow API", version="0.1.0")


class RecommendationRequest(BaseModel):
    state: str = Field(..., description="Two-letter state code such as CA or TX.")
    top_k: int = Field(default=5, ge=1, le=20)
    max_predicted_failure_probability: float = Field(default=0.35, ge=0.0, le=1.0)


class RagQueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=10)
    use_llm: bool = False


@app.on_event("startup")
def startup_event() -> None:
    build_recommendation_snapshot()
    build_rag_index()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/overview")
def overview() -> dict[str, object]:
    return load_overview_summary()


@app.post("/recommendations")
def recommendations(request: RecommendationRequest) -> dict[str, object]:
    results = recommend_stations(
        state=request.state,
        top_k=request.top_k,
        max_predicted_failure_probability=request.max_predicted_failure_probability,
    )
    return {"results": results}


@app.post("/rag/query")
def rag_query(request: RagQueryRequest) -> dict[str, object]:
    return answer_query(request.query, top_k=request.top_k, use_llm=request.use_llm)
