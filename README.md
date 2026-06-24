# ETL-RAG Observability Platform

A personal full-stack project for monitoring ETL pipelines, RAG workflows, and agent-based workflow execution.

I built this project to practice modern backend, data, and AI engineering concepts in one system. The main goal is to show how structured data pipelines and AI retrieval workflows can be tracked, evaluated, and reviewed through a simple dashboard.

---

## Problem

Data and AI workflows can fail in ways that are not always obvious.

Examples:
- an ETL pipeline may complete but still produce poor-quality data
- a RAG system may return an answer using weak or irrelevant retrieved context
- workflow failures may be hard to trace across multiple services

This project explores how these workflows can be monitored with run history, quality signals, risk flags, and step-level traces.

---

## Key Features

### ETL Pipeline

- Upload and process CSV datasets
- Profile columns, data types, missing values, and unique values
- Detect basic anomalies in datasets
- Calculate data quality scores
- Track ETL run status, timing, and metadata

### RAG Pipeline

- Upload text documents for retrieval
- Chunk and embed documents
- Store embeddings in ChromaDB
- Query documents using semantic retrieval
- Track retrieved chunks, sources, timing, and warning flags

### Observability Dashboard

- View ETL and RAG activity in one dashboard
- Track health scores, failures, and high-risk queries
- Review processing-time and quality trends
- Drill into individual ETL and RAG runs

### Agentic Workflow Layer

- Coordinate ETL and RAG workflows through an agent service
- Track planner, ETL, RAG, evaluator, and report steps
- Support human approval, reject, and retry flow
- Add a LangGraph-based workflow path for agent orchestration

---

## Architecture

```text
Streamlit Dashboard
        |
        v
Observability Service
        |
        +--> ETL Service
        |
        +--> RAG Service
        |
        +--> Agent Service
                |
                +--> Planner Agent
                +--> ETL Agent
                +--> RAG Agent
                +--> Evaluator Agent
                +--> Human Approval
                +--> Report Agent
```

---

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pandas

### AI / Data
- LangChain
- LangGraph
- ChromaDB
- Sentence Transformers

### Frontend
- Streamlit
- Plotly
- Pandas

### Tooling
- Docker
- Docker Compose
- Pytest
- Ruff
- Playwright

---

## What This Project Shows

### Backend Engineering
- FastAPI service design
- REST API development
- PostgreSQL data persistence
- Background processing
- Error handling and status tracking

### Data Engineering
- CSV ingestion
- ETL-style processing
- Data profiling
- Data quality checks
- Anomaly detection

### AI Engineering
- RAG workflow implementation
- Vector search
- Retrieval metadata tracking
- Basic retrieval risk evaluation
- LangGraph workflow experimentation

### Platform / Observability
- Microservice-based design
- Run tracking across services
- Health score calculation
- Failure monitoring
- Agent workflow tracing

### Testing
- Unit tests for ETL, RAG, and agent logic
- API health checks
- Frontend smoke tests
- Linting and coverage setup

---

## Screenshots

Add screenshots here:

- Overview dashboard
- ETL run details
- RAG response with retrieved chunks
- Agent workflow trace
- Failure monitoring page

---

## Project Status

This is an ongoing personal project focused on backend engineering, data pipeline reliability, RAG observability, and agentic workflow orchestration.