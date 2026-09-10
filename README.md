# Orpheus RAG

Portable deployment assets for a private RAGFlow-based knowledge system.

## Design goals

- Keep cloud hosts disposable.
- Keep business data and deployment recipes portable.
- Keep secrets, model weights, caches, logs, backups, and private documents out of Git.
- Prefer reproducible builds over copying mutable container layers.
- Keep model serving replaceable so Embedding/Reranker models can be upgraded later.

## Planned layout

```text
configs/        Compose overrides and non-secret configuration
scripts/        Bootstrap, backup, restore, and migration scripts
images/         Reproducible Dockerfiles for custom images
docs/           Architecture and recovery notes
.github/        CI workflows, including container-image mirroring
```

## Runtime data policy

The Git repository is for recipes, not runtime data.

Typical host layout:

```text
/opt/orpheus-rag/            deployment assets
/data/orpheus-rag/persistent business state
/data/orpheus-rag/rebuildable models, caches, logs, temporary files
```

Do not commit API keys, passwords, private documents, database dumps, model weights, exported Docker images, or RAGFlow runtime data.

## Current stack target

- RAGFlow v0.27.1
- NVIDIA L20 class GPU host
- Custom RAGFlow GPU image with PyTorch/CUDA runtime baked in
- Elasticsearch + MySQL + Valkey + Silo
- Local Embedding/Reranker serving, with model backend kept replaceable
- External LLM API
- External VLM API when economical

## Recovery principle

Balanced recovery:

- Move deployment recipes, MySQL backup, object data, and Elasticsearch snapshot.
- Re-pull/rebuild ordinary images and model weights when practical.
- Keep large reproducible artifacts outside Git.
