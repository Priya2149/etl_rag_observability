from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from time import perf_counter

from app.db import get_db
from app.models import RagDocument, RagQueryRun
from app.services.ingest import save_uploaded_file, ingest_document
from app.services.retrieve import query_documents

router = APIRouter(prefix="/rag", tags=["RAG"])

class QueryRequest(BaseModel):
    query: str

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported right now.")

    file_path = save_uploaded_file(file)
    ingest_result = ingest_document(file_path)

    document = RagDocument(
        filename=file.filename,
        filepath=file_path,
        status="ingested"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "document_id": document.id,
        "filename": document.filename,
        "status": document.status,
        "chunk_count": ingest_result["chunk_count"]
    }

@router.post("/ask")
def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    started_at = perf_counter()

    try:
        result = query_documents(request.query)
    except Exception as exc:
        processing_time_ms = round((perf_counter() - started_at) * 1000)
        run = RagQueryRun(
            query=request.query,
            answer=None,
            retrieved_chunks=None,
            sources=json.dumps([]),
            chunks_used=0,
            processing_time_ms=processing_time_ms,
            retrieved_count=0,
            source_files=json.dumps([]),
            best_distance=None,
            risk_level="high",
            evaluation_status="failed",
            warning_flags=json.dumps(["query_execution_failed"]),
            status="failed",
            error_message=str(exc),
        )
        db.add(run)
        db.commit()

        raise HTTPException(status_code=500, detail=str(exc)) from exc

    processing_time_ms = round((perf_counter() - started_at) * 1000)
    sources = result["source_files"]

    run = RagQueryRun(
        query=request.query,
        answer=result["answer"],
        retrieved_chunks=json.dumps(result["retrieved_chunks"]),
        sources=json.dumps(sources),
        chunks_used=result["chunks_used"],
        processing_time_ms=processing_time_ms,
        retrieved_count=result["retrieved_count"],
        source_files=json.dumps(sources),
        best_distance=result["best_distance"],
        risk_level=result["risk_level"],
        evaluation_status=result["evaluation_status"],
        warning_flags=json.dumps(result["warning_flags"]),
        status="completed",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    retrieval_info = {
        "chunks_used": result["chunks_used"],
        "retrieved_count": result["retrieved_count"],
        "best_distance": result["best_distance"],
        "sources": sources,
    }
    evaluation = {
        "risk_level": result["risk_level"],
        "evaluation_status": result["evaluation_status"],
        "warning_flags": result["warning_flags"],
    }

    return {
        "run_id": run.id,
        "query": request.query,
        "answer": result["answer"],
        "retrieved_chunks": result["retrieved_chunks"],
        "chunks_used": result["chunks_used"],
        "retrieved_count": result["retrieved_count"],
        "source_files": sources,
        "sources": sources,
        "best_distance": result["best_distance"],
        "risk_level": result["risk_level"],
        "evaluation_status": result["evaluation_status"],
        "warning_flags": result["warning_flags"],
        "processing_time_ms": processing_time_ms,
        "retrieval_info": retrieval_info,
        "evaluation": evaluation,
    }

@router.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(RagDocument).order_by(RagDocument.created_at.desc()).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "filepath": doc.filepath,
            "status": doc.status,
            "created_at": doc.created_at
        }
        for doc in docs
    ]

@router.get("/runs")
def get_runs(db: Session = Depends(get_db)):
    runs = db.query(RagQueryRun).order_by(RagQueryRun.created_at.desc()).all()
    return [
        {
            "id": run.id,
            "query": run.query,
            "answer": run.answer,
            "chunks_used": run.chunks_used,
            "retrieved_count": run.retrieved_count,
            "source_files": json.loads(run.source_files) if run.source_files else [],
            "best_distance": run.best_distance,
            "risk_level": run.risk_level,
            "evaluation_status": run.evaluation_status,
            "warning_flags": json.loads(run.warning_flags) if run.warning_flags else [],
            "processing_time_ms": run.processing_time_ms,
            "status": run.status,
            "created_at": run.created_at
        }
        for run in runs
    ]

@router.get("/runs/{run_id}")
def get_run_details(run_id: int, db: Session = Depends(get_db)):
    run = db.query(RagQueryRun).filter(RagQueryRun.id == run_id).first()

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": run.id,
        "query": run.query,
        "answer": run.answer,
        "status": run.status,
        "chunks_used": run.chunks_used,
        "retrieved_count": run.retrieved_count,
        "source_files": json.loads(run.source_files) if run.source_files else [],
        "best_distance": run.best_distance,
        "risk_level": run.risk_level,
        "evaluation_status": run.evaluation_status,
        "warning_flags": json.loads(run.warning_flags) if run.warning_flags else [],
        "processing_time_ms": run.processing_time_ms,
        "sources": json.loads(run.sources) if run.sources else [],
        "retrieved_chunks": json.loads(run.retrieved_chunks) if run.retrieved_chunks else [],
        "error_message": run.error_message,
        "created_at": run.created_at
    }
