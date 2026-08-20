# Repository Working Agreement

## Current Architecture

This repository is a Docker Compose application with five Python services and one shared PostgreSQL database:

- `etl_service`: FastAPI CSV ingestion, profiling, anomaly detection, quality scoring, and ETL run persistence.
- `rag_service`: FastAPI text ingestion, Sentence Transformers embeddings, ChromaDB retrieval, retrieval evaluation, and RAG run persistence.
- `observability_service`: FastAPI read-only summaries over ETL and RAG run data in PostgreSQL.
- `agent_service`: FastAPI workflow orchestration, ETL/RAG HTTP tool clients, step tracing, human approval, and the existing LangGraph workflow path.
- `frontend`: Streamlit dashboard for ETL, RAG, observability, failures, and agent workflows.
- `db`: PostgreSQL shared by the backend services. ChromaDB storage remains owned by `rag_service`.
- `shared/llm`: Provider-independent LLM configuration, typed responses, retries, local retrieval-only generation, and the OpenAI provider. It is packaged into the RAG and agent images but does not bypass their HTTP/data boundaries.

Keep service boundaries intact. The mounted FastAPI routers under each service's `app/routes` directory are the API source of truth. Cross-service operations should use the existing HTTP clients rather than importing another service's internals.

Keep OpenAI initialization lazy and keep `LLM_PROVIDER=none` usable without a key or network access. Automated tests must use fake provider clients and must never call paid APIs.

## Common Commands

Create local configuration when needed:

```powershell
Copy-Item .env.example .env
```

Install test tooling and service dependencies into an active virtual environment:

```powershell
python -m pip install -r requirements-dev.txt
python -m pip install -r etl_service/requirements.txt -r rag_service/requirements.txt -r observability_service/requirements.txt -r agent_service/requirements.txt -r frontend/requirements.txt
python -m playwright install chromium
```

Build and run the full stack:

```powershell
docker compose up --build
```

Compose uses project-scoped container and volume names. For disposable integration testing, use a distinct project name and remove only that project's volume afterward:

```powershell
docker compose -p etl-rag-baseline up --build -d
docker compose -p etl-rag-baseline down --volumes
```

Run the complete test suite after the stack is healthy:

```powershell
python -m pytest
```

Run focused unit tests while developing:

```powershell
python -m pytest tests/etl tests/rag tests/agent
python -m pytest tests/llm tests/rag
```

Run static checks:

```powershell
python -m ruff check .
python -m mypy etl_service rag_service observability_service agent_service
```

## Change Rules

- Preserve existing working APIs, persistence, dashboard behavior, and workflow traces.
- Extend the current architecture incrementally; avoid service rewrites or unrelated refactors.
- Keep the mounted route modules as the source of truth and avoid duplicate API implementations.
- Never commit `.env`, API keys, passwords, tokens, or other secrets. Update `.env.example` only with safe placeholders.
- Run the most relevant unit tests after each change and the full suite when integration dependencies are available.
- Do not claim a feature, migration, or test suite is complete unless its behavior has been verified.
- Record environmental blockers separately from code failures instead of weakening tests to make them pass.
