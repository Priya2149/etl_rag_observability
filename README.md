# ETL-RAG Observability Platform

A backend-focused microservices project for running ETL pipelines and RAG-based document workflows, with built-in run tracking and observability.

---

## Overview

This project explores how modern backend systems handle both structured and unstructured data workflows while maintaining visibility into how those workflows execute.

It combines:

- **ETL pipelines** for processing structured datasets (CSV)
- **RAG (Retrieval-Augmented Generation)** for querying document data
- **Observability features** to track runs, results, and performance

The goal is to simulate a simple platform where data workflows can be executed through APIs and monitored through stored run metadata.

---

## Problem Statement

In real-world systems, data pipelines and document-based workflows often lack visibility. Failures, poor data quality, or incorrect retrieval results can be difficult to trace.

This project focuses on:

- making workflows easier to execute via APIs  
- tracking execution results and metadata  
- improving visibility into data processing and retrieval behavior  

---

## Features

### ETL Pipeline (Structured Data)

- Upload CSV datasets via API  
- Perform schema profiling (columns, types, missing values)  
- Detect anomalies and compute basic data quality metrics  
- Store pipeline run results in PostgreSQL  
- Background processing with run status tracking  

---

### RAG Pipeline (Unstructured Data)

- Upload text documents for ingestion  
- Chunk and embed documents using sentence-transformers  
- Store embeddings in ChromaDB  
- Perform semantic search based on user queries  
- Return relevant document context as responses  
- Store query runs and retrieved chunks for traceability  

---

### Observability & Run Tracking

- Track execution status (`pending`, `processing`, `completed`, `failed`)  
- Store processing time for each run  
- Capture metadata such as:
  - retrieved chunks
  - source documents
  - anomaly summaries
- Access historical runs via API  

---

## Architecture

The system follows a microservices-based design:

- **ETL Service**  
  Handles structured data ingestion and processing  

- **RAG Service**  
  Handles document ingestion and semantic retrieval  

- **PostgreSQL**  
  Stores pipeline runs, query results, and metadata  

Each service runs independently and communicates via REST APIs.

---

## Tech Stack

- **Backend:** FastAPI (Python)  
- **Data Processing:** Pandas  
- **RAG:** LangChain, ChromaDB, Sentence Transformers  
- **Database:** PostgreSQL  
- **Containerization:** Docker, Docker Compose  

---

## API Overview

### ETL Service

- `POST /etl/upload` – Upload and process dataset  
- `GET /etl/runs` – List all pipeline runs  
- `GET /etl/runs/{id}` – Get detailed run information  

---

### RAG Service

- `POST /rag/upload` – Upload document for ingestion  
- `POST /rag/ask` – Query documents  
- `GET /rag/runs` – List query runs  
- `GET /rag/runs/{id}` – Get query run details  

---

## Current Scope

This project focuses on backend system design and data workflow execution.

It does not currently include:
- authentication/authorization  
- frontend dashboard (planned)  
- production-scale deployment  

---

## Future Improvements

- Add LLM-based answer generation for RAG responses  
- Build a dashboard for visualizing pipeline and query metrics  
- Improve retrieval quality and ranking  
- Add centralized observability service across ETL and RAG  
- Support additional data sources and formats  

---

## Why This Project

This project was built to better understand:

- ETL pipeline design in Python  
- Retrieval-based systems (RAG)  
- Microservices architecture using FastAPI  
- Observability and run tracking in backend systems  

---

## Getting Started (Local Setup)

```bash
docker compose up --build
