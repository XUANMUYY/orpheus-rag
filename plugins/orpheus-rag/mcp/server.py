from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer

RAGFLOW_BASE_URL = os.environ.get("RAGFLOW_BASE_URL", "http://127.0.0.1:9380").rstrip("/")
RAGFLOW_API_KEY = os.environ.get("RAGFLOW_API_KEY", "")
HOST = os.environ.get("ORPHEUS_MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("ORPHEUS_MCP_PORT", "8090"))

mcp = MCPServer(
    "Orpheus RAG",
    instructions=(
        "This server provides read-only access to the user's private RAGFlow knowledge base. "
        "Use its tools only when the user explicitly asks to search, query, verify against, or use the private knowledge base. "
        "Never imply that a source or page exists unless it is present in the returned metadata."
    ),
)


def _headers() -> dict[str, str]:
    if not RAGFLOW_API_KEY:
        raise RuntimeError("RAGFLOW_API_KEY is not configured on the server")
    return {"Authorization": f"Bearer {RAGFLOW_API_KEY}"}


def _check_response(response: httpx.Response) -> dict[str, Any]:
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") not in (None, 0):
        raise RuntimeError(payload.get("message") or f"RAGFlow error code {payload.get('code')}")
    return payload


@mcp.tool()
def list_datasets(name: str | None = None, page: int = 1, page_size: int = 100) -> dict[str, Any]:
    """List RAGFlow datasets visible to the configured private account. Use only for private-knowledge-base requests."""
    params: dict[str, Any] = {
        "page": max(1, page),
        "page_size": min(max(1, page_size), 100),
    }
    if name:
        params["name"] = name

    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{RAGFLOW_BASE_URL}/api/v1/datasets",
            headers=_headers(),
            params=params,
        )
    payload = _check_response(response)
    return {
        "datasets": payload.get("data", []),
        "total_datasets": payload.get("total_datasets", payload.get("total", 0)),
    }


@mcp.tool()
def search_knowledge(
    question: str,
    dataset_ids: list[str] | None = None,
    document_ids: list[str] | None = None,
    page_size: int = 8,
    similarity_threshold: float = 0.2,
    vector_similarity_weight: float = 0.3,
    keyword: bool = True,
    knn_top_k: int = 1024,
) -> dict[str, Any]:
    """Retrieve relevant source chunks from the private Orpheus RAGFlow knowledge base. Call only when the user explicitly requests private knowledge-base retrieval."""
    if not question.strip():
        raise ValueError("question must not be empty")

    resolved_dataset_ids = dataset_ids
    if not resolved_dataset_ids:
        listed = list_datasets(page=1, page_size=100)
        resolved_dataset_ids = [d["id"] for d in listed.get("datasets", []) if d.get("id")]
        if not resolved_dataset_ids:
            return {
                "question": question,
                "dataset_ids": [],
                "total": 0,
                "chunks": [],
                "message": "No datasets are currently available in the private knowledge base.",
            }

    body: dict[str, Any] = {
        "dataset_ids": resolved_dataset_ids,
        "question": question,
        "page": 1,
        "page_size": min(max(1, page_size), 30),
        "similarity_threshold": min(max(similarity_threshold, 0.0), 1.0),
        "vector_similarity_weight": min(max(vector_similarity_weight, 0.0), 1.0),
        "keyword": keyword,
        "knn_top_k": min(max(1, knn_top_k), 2048),
    }
    if document_ids:
        body["document_ids"] = document_ids

    with httpx.Client(timeout=90.0) as client:
        response = client.post(
            f"{RAGFLOW_BASE_URL}/api/v1/retrieval",
            headers={**_headers(), "Content-Type": "application/json"},
            json=body,
        )
    payload = _check_response(response)
    data = payload.get("data", payload)

    return {
        "question": question,
        "dataset_ids": resolved_dataset_ids,
        "result": data,
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=HOST,
        port=PORT,
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
    )
