from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.utils.config import ROOT_DIR, get_settings
from src.utils.filesystem import rag_data_root
from src.utils.assets import read_csv_asset


def build_rag_index() -> dict[str, Path]:
    documents = _load_documents()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(documents["content"])

    rag_root = rag_data_root()
    docs_path = rag_root / "rag_documents.csv"
    index_path = rag_root / "rag_index.joblib"
    metadata_path = rag_root / "rag_index_metadata.json"

    documents.to_csv(docs_path, index=False)
    joblib.dump({"vectorizer": vectorizer, "matrix": matrix, "documents": documents}, index_path)
    metadata_path.write_text(
        json.dumps({"document_count": int(len(documents)), "sources": documents["source_type"].value_counts().to_dict()}, indent=2),
        encoding="utf-8",
    )
    return {"documents": docs_path, "index": index_path, "metadata": metadata_path}


def retrieve_documents(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    index_bundle = _load_index()
    vectorizer = index_bundle["vectorizer"]
    matrix = index_bundle["matrix"]
    documents = index_bundle["documents"]

    query_vector = vectorizer.transform([query])
    similarity_scores = cosine_similarity(query_vector, matrix).flatten()
    top_indices = similarity_scores.argsort()[::-1][:top_k]

    results = []
    for index in top_indices:
        row = documents.iloc[index].to_dict()
        row["score"] = round(float(similarity_scores[index]), 4)
        results.append(row)
    return results


def answer_query(query: str, top_k: int = 3, use_llm: bool = False) -> dict[str, Any]:
    retrieved = retrieve_documents(query, top_k=top_k)
    answer = _build_extract_answer(query, retrieved)

    if use_llm and get_settings().groq_api_key:
        llm_answer = _generate_groq_answer(query, retrieved)
        if llm_answer:
            answer = llm_answer

    return {"query": query, "answer": answer, "sources": retrieved}


def _load_documents() -> pd.DataFrame:
    notes = read_csv_asset("synthetic", "maintenance_notes.csv")
    tickets = read_csv_asset("synthetic", "maintenance_tickets.csv")

    note_docs = notes.rename(columns={"note_id": "document_id", "note_text": "content"})[
        ["document_id", "station_id", "ticket_id", "content"]
    ].copy()
    note_docs["source_type"] = "maintenance_note"
    note_docs["title"] = "Maintenance Note"

    ticket_docs = tickets.copy()
    ticket_docs["document_id"] = ticket_docs["ticket_id"]
    ticket_docs["content"] = ticket_docs["summary"] + " Resolution: " + ticket_docs["resolution_code"].fillna("unknown")
    ticket_docs["source_type"] = "maintenance_ticket"
    ticket_docs["title"] = "Maintenance Ticket"
    ticket_docs = ticket_docs[["document_id", "station_id", "failure_event_id", "content", "source_type", "title"]]
    ticket_docs["ticket_id"] = ticket_docs["document_id"]

    sop_docs = []
    for sop_path in sorted((ROOT_DIR / "docs" / "sops").glob("*.md")):
        sop_docs.append(
            {
                "document_id": sop_path.stem,
                "station_id": "",
                "ticket_id": "",
                "content": sop_path.read_text(encoding="utf-8"),
                "source_type": "sop",
                "title": sop_path.stem.replace("_", " ").title(),
            }
        )
    sop_df = pd.DataFrame(sop_docs)

    combined = pd.concat(
        [
            note_docs[["document_id", "station_id", "ticket_id", "content", "source_type", "title"]],
            ticket_docs[["document_id", "station_id", "ticket_id", "content", "source_type", "title"]],
            sop_df[["document_id", "station_id", "ticket_id", "content", "source_type", "title"]],
        ],
        ignore_index=True,
    )
    return combined.fillna("")


def _load_index() -> dict[str, Any]:
    index_path = rag_data_root() / "rag_index.joblib"
    if not index_path.exists():
        build_rag_index()
    return joblib.load(index_path)


def _build_extract_answer(query: str, retrieved: list[dict[str, Any]]) -> str:
    if not retrieved:
        return "No relevant maintenance or SOP documents were found for that query."
    snippets = [f"{item['title']}: {item['content'][:220]}" for item in retrieved]
    return (
        f"Top grounded guidance for '{query}': "
        + " | ".join(snippets)
    )


def _generate_groq_answer(query: str, retrieved: list[dict[str, Any]]) -> str | None:
    try:
        from groq import Groq

        client = Groq(api_key=get_settings().groq_api_key)
        context = "\n\n".join([f"{item['title']} ({item['source_type']}): {item['content']}" for item in retrieved])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a grounded EV charging operations assistant. "
                        "Answer only from the provided context and mention when evidence is limited."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {query}\n\nContext:\n{context}",
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception:
        return None
