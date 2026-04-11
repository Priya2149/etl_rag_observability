from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from ..db import get_db
from ..models import RagDocument, RagQueryRun
from ..services.ingest import save_uploaded_file, ingest_document
from ..services.retrieve import query_documents

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
    try:
        result = query_documents(request.query)

        run = RagQueryRun(
            query=request.query,
            answer=result["answer"],
            retrieved_chunks=json.dumps(result["retrieved_chunks"]),
            retrieved_count=result["retrieved_count"],
            source_files=json.dumps(result["source_files"]),
            best_distance=result["best_distance"],
            risk_level=result["risk_level"],
            evaluation_status=result["evaluation_status"],
            warning_flags=json.dumps(result["warning_flags"]),
            status="completed"
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        return {
            "run_id": run.id,
            "query": request.query,
            "answer": result["answer"],
            "retrieved_count": result["retrieved_count"],
            "source_files": result["source_files"],
            "best_distance": result["best_distance"],
            "risk_level": result["risk_level"],
            "evaluation_status": result["evaluation_status"],
            "warning_flags": result["warning_flags"],
            "retrieved_chunks": result["retrieved_chunks"]
        }

    except Exception as e:
        run = RagQueryRun(
            query=request.query,
            answer=None,
            retrieved_chunks=None,
            retrieved_count=0,
            source_files=json.dumps([]),
            best_distance=None,
            risk_level="high",
            evaluation_status="failed",
            warning_flags=json.dumps(["Query execution failed"]),
            status="failed",
            error_message=str(e)
        )
        db.add(run)
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))


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
            "retrieved_count": run.retrieved_count,
            "source_files": json.loads(run.source_files) if run.source_files else [],
            "best_distance": run.best_distance,
            "risk_level": run.risk_level,
            "evaluation_status": run.evaluation_status,
            "warning_flags": json.loads(run.warning_flags) if run.warning_flags else [],
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
        "retrieved_count": run.retrieved_count,
        "source_files": json.loads(run.source_files) if run.source_files else [],
        "best_distance": run.best_distance,
        "risk_level": run.risk_level,
        "evaluation_status": run.evaluation_status,
        "warning_flags": json.loads(run.warning_flags) if run.warning_flags else [],
        "retrieved_chunks": json.loads(run.retrieved_chunks) if run.retrieved_chunks else [],
        "status": run.status,
        "error_message": run.error_message,
        "created_at": run.created_at
    }