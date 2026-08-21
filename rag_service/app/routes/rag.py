import json
from time import perf_counter

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RagDocument, RagQueryRun
from app.services.answer import build_rag_request, generate_rag_answer
from app.services.ingest import ingest_document, save_uploaded_file
from app.services.retrieve import query_documents
from shared.llm import (
    LLMConfigurationError,
    LLMError,
    LLMProviderError,
    LLMRateLimitError,
    get_configured_provider,
)

router = APIRouter(prefix="/rag", tags=["RAG"])

class QueryRequest(BaseModel):
    query: str


def _provider_status_code(exc: Exception) -> int:
    if isinstance(exc, LLMConfigurationError):
        return 503
    if isinstance(exc, LLMRateLimitError):
        return 429
    if isinstance(exc, LLMProviderError):
        return 502
    return 500


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"

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
        provider = get_configured_provider()
        result = query_documents(request.query)
        generation = generate_rag_answer(request.query, result, provider=provider)
        result["answer"] = generation.output.answer
        result["sources"] = generation.output.sources
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

        raise HTTPException(
            status_code=_provider_status_code(exc), detail=str(exc)
        ) from exc

    processing_time_ms = round((perf_counter() - started_at) * 1000)
    sources = result["sources"]
    source_files = result["source_files"]

    run = RagQueryRun(
        query=request.query,
        answer=result["answer"],
        retrieved_chunks=json.dumps(result["retrieved_chunks"]),
        sources=json.dumps(sources),
        chunks_used=result["chunks_used"],
        processing_time_ms=processing_time_ms,
        retrieved_count=result["retrieved_count"],
        source_files=json.dumps(source_files),
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
        "source_files": source_files,
        "sources": sources,
        "best_distance": result["best_distance"],
        "risk_level": result["risk_level"],
        "evaluation_status": result["evaluation_status"],
        "warning_flags": result["warning_flags"],
        "processing_time_ms": processing_time_ms,
        "request_id": generation.request_id,
        "provider": generation.provider,
        "model": generation.model,
        "usage": generation.usage.model_dump(),
        "retrieval_info": retrieval_info,
        "evaluation": evaluation,
    }


@router.post("/search")
def search_documents(request: QueryRequest):
    """Expose semantic retrieval without invoking an LLM or recording a RAG answer."""
    try:
        result = query_documents(request.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Document search failed.") from exc

    return {
        "query": request.query,
        "retrieved_chunks": result["retrieved_chunks"],
        "retrieved_count": result["retrieved_count"],
        "chunks_used": result["chunks_used"],
        "source_files": result["source_files"],
        "best_distance": result["best_distance"],
        "risk_level": result["risk_level"],
        "evaluation_status": result["evaluation_status"],
        "warning_flags": result["warning_flags"],
    }


@router.post("/ask/stream")
def ask_question_stream(request: QueryRequest):
    try:
        provider = get_configured_provider()
        retrieval = query_documents(request.query)
        llm_request = build_rag_request(request.query, retrieval)
    except LLMError as exc:
        raise HTTPException(
            status_code=_provider_status_code(exc), detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    def event_stream():
        yield _sse(
            "metadata",
            {
                "provider": provider.name,
                "model": provider.model,
                "sources": retrieval["source_files"],
            },
        )
        try:
            for event in provider.stream(llm_request):
                if event.type == "delta":
                    yield _sse("delta", {"text": event.delta})
                else:
                    yield _sse(
                        "completed",
                        {
                            "request_id": event.request_id,
                            "provider": event.provider,
                            "model": event.model,
                            "sources": retrieval["source_files"],
                            "usage": event.usage.model_dump(),
                        },
                    )
        except LLMError as exc:
            yield _sse("error", {"detail": str(exc)})
        # The SSE response has already started, so unexpected errors must become
        # a safe terminal event instead of an unhandled connection traceback.
        except Exception:  # noqa: BLE001
            yield _sse("error", {"detail": "Streaming generation failed."})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )

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
