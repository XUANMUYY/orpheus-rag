---
name: query-orpheus-knowledge
description: Retrieve information from the user's private Orpheus RAGFlow knowledge base only when the user explicitly asks to search, query, verify against, or use that knowledge base.
---

Use this skill only when the user explicitly requests private-knowledge-base retrieval, for example by saying to search/query/check/verify/use their RAG, RAGFlow, Orpheus knowledge base, or private documents.

Do not activate this skill for ordinary conversation, general knowledge questions, or web research unless the user explicitly asks to consult the private knowledge base.

Workflow:
1. If the target dataset is unknown, call `list_datasets` first.
2. Call `search_knowledge` with the user's actual question. Restrict by dataset IDs or document IDs when the user specifies a scope.
3. Prefer the returned source chunks over unsupported inference.
4. Preserve source metadata such as document name, document ID, chunk ID, page number, and similarity scores when present.
5. Never invent a page number or source locator. If RAGFlow does not return a page field, cite the document/chunk metadata that is available.
6. If retrieval returns no useful evidence, say that the private knowledge base did not produce a supporting result instead of filling the gap from memory.
7. Treat the plugin as read-only. Do not upload, modify, delete, rename, parse, or reconfigure datasets or documents.
