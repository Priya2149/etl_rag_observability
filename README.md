# ETL-RAG Observability Platform

This is an ongoing backend-focused project for running ETL pipelines and RAG-based document workflows, with built-in run tracking and observability.

---

## Overview

This project handles both structured and unstructured data workflows through APIs and tracks how those workflows execute.

It includes:

- an ETL pipeline for processing CSV datasets  
- a RAG pipeline for querying document data  
- run tracking and metadata storage for observability  

The system is designed to execute data workflows and provide visibility into their results and behavior.

---

## Features

### ETL Pipeline (Structured Data)

- Upload CSV datasets via API  
- Perform schema profiling (columns, types, missing values)  
- Detect anomalies and compute data quality metrics  
- Store pipeline run results in PostgreSQL  
- Execute processing in the background with run status tracking  

---

### RAG Pipeline (Unstructured Data)

- Upload text documents for ingestion  
- Chunk and embed documents using sentence-transformers  
- Store embeddings in ChromaDB  
- Perform semantic search based on user queries  
- Return relevant document context as responses  
- Store query runs and retrieved chunks  

---

### Run Tracking & Observability

- Track execution status (`pending`, `processing`, `completed`, `failed`)  
- Store processing time for each run  
- Capture metadata such as:
  - retrieved chunks  
  - source documents  
  - anomaly summaries  
- Access historical runs through API endpoints  

---

## Architecture

The system is organized as microservices:

- **ETL Service** – handles structured data processing  
- **RAG Service** – handles document ingestion and retrieval  
- **PostgreSQL** – stores run data and metadata  

Each service runs independently and exposes REST APIs.

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
- `GET /etl/runs` – List pipeline runs  
- `GET /etl/runs/{id}` – Get detailed run information  

---

### RAG Service

- `POST /rag/upload` – Upload document  
- `POST /rag/ask` – Query documents  
- `GET /rag/runs` – List query runs  
- `GET /rag/runs/{id}` – Get query run details  

---

## Project Scope

This project focuses on backend system design, data processing workflows, and tracking execution behavior through APIs and stored metadata.
