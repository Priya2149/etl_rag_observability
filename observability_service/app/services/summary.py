from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import PipelineRun, RagDocument, RagQueryRun


def calculate_etl_health_score(avg_quality_score, failed_runs, total_runs):
    if total_runs == 0:
        return 100

    score = 100

    if avg_quality_score is not None:
        score -= max(0, 100 - float(avg_quality_score))

    failure_rate = failed_runs / total_runs if total_runs > 0 else 0
    score -= failure_rate * 30

    return round(max(score, 0), 2)


def calculate_rag_health_score(failed_queries, total_queries, high_risk_queries):
    if total_queries == 0:
        return 100

    score = 100

    failure_rate = failed_queries / total_queries if total_queries > 0 else 0
    high_risk_rate = high_risk_queries / total_queries if total_queries > 0 else 0

    score -= failure_rate * 40
    score -= high_risk_rate * 35

    return round(max(score, 0), 2)


def get_etl_summary(db: Session):
    total_runs = db.query(func.count(PipelineRun.id)).scalar() or 0
    completed_runs = db.query(func.count(PipelineRun.id)).filter(PipelineRun.status == "completed").scalar() or 0
    failed_runs = db.query(func.count(PipelineRun.id)).filter(PipelineRun.status == "failed").scalar() or 0
    processing_runs = db.query(func.count(PipelineRun.id)).filter(PipelineRun.status == "processing").scalar() or 0

    avg_quality_score = db.query(func.avg(PipelineRun.quality_score)).scalar()
    avg_processing_time = db.query(func.avg(PipelineRun.processing_time_ms)).scalar()

    recent_runs = (
        db.query(PipelineRun)
        .order_by(PipelineRun.created_at.desc())
        .limit(7)
        .all()
    )

    health_score = calculate_etl_health_score(avg_quality_score, failed_runs, total_runs)

    trends = [
        {
            "id": run.id,
            "quality_score": run.quality_score,
            "processing_time_ms": run.processing_time_ms,
            "status": run.status,
            "created_at": run.created_at,
        }
        for run in reversed(recent_runs)
    ]

    return {
        "total_runs": total_runs,
        "completed_runs": completed_runs,
        "failed_runs": failed_runs,
        "processing_runs": processing_runs,
        "avg_quality_score": round(float(avg_quality_score), 2) if avg_quality_score is not None else None,
        "avg_processing_time_ms": round(float(avg_processing_time), 2) if avg_processing_time is not None else None,
        "health_score": health_score,
        "recent_runs": [
            {
                "id": run.id,
                "filename": run.filename,
                "status": run.status,
                "quality_score": run.quality_score,
                "processing_time_ms": run.processing_time_ms,
                "created_at": run.created_at,
            }
            for run in recent_runs
        ],
        "trends": trends,
    }


def get_rag_summary(db: Session):
    total_documents = db.query(func.count(RagDocument.id)).scalar() or 0
    total_queries = db.query(func.count(RagQueryRun.id)).scalar() or 0
    completed_queries = db.query(func.count(RagQueryRun.id)).filter(RagQueryRun.status == "completed").scalar() or 0
    failed_queries = db.query(func.count(RagQueryRun.id)).filter(RagQueryRun.status == "failed").scalar() or 0
    processing_queries = db.query(func.count(RagQueryRun.id)).filter(RagQueryRun.status == "processing").scalar() or 0
    high_risk_queries = db.query(func.count(RagQueryRun.id)).filter(RagQueryRun.risk_level == "high").scalar() or 0

    avg_chunks_used = db.query(func.avg(RagQueryRun.chunks_used)).scalar()
    avg_processing_time = db.query(func.avg(RagQueryRun.processing_time_ms)).scalar()

    recent_queries = (
        db.query(RagQueryRun)
        .order_by(RagQueryRun.created_at.desc())
        .limit(7)
        .all()
    )

    health_score = calculate_rag_health_score(failed_queries, total_queries, high_risk_queries)

    trends = [
        {
            "id": run.id,
            "chunks_used": run.chunks_used,
            "retrieved_count": run.retrieved_count,
            "processing_time_ms": run.processing_time_ms,
            "risk_level": run.risk_level,
            "created_at": run.created_at,
        }
        for run in reversed(recent_queries)
    ]

    return {
        "total_documents": total_documents,
        "total_queries": total_queries,
        "completed_queries": completed_queries,
        "failed_queries": failed_queries,
        "processing_queries": processing_queries,
        "high_risk_queries": high_risk_queries,
        "avg_chunks_used": round(float(avg_chunks_used), 2) if avg_chunks_used is not None else None,
        "avg_processing_time_ms": round(float(avg_processing_time), 2) if avg_processing_time is not None else None,
        "health_score": health_score,
        "recent_queries": [
            {
                "id": run.id,
                "query": run.query,
                "status": run.status,
                "chunks_used": run.chunks_used,
                "retrieved_count": run.retrieved_count,
                "processing_time_ms": run.processing_time_ms,
                "risk_level": run.risk_level,
                "evaluation_status": run.evaluation_status,
                "created_at": run.created_at,
            }
            for run in recent_queries
        ],
        "trends": trends,
    }


def get_recent_failures(db: Session):
    etl_failures = (
        db.query(PipelineRun)
        .filter(PipelineRun.status == "failed")
        .order_by(PipelineRun.created_at.desc())
        .limit(5)
        .all()
    )

    rag_failures = (
        db.query(RagQueryRun)
        .filter(
            (RagQueryRun.status == "failed") |
            (RagQueryRun.risk_level == "high")
        )
        .order_by(RagQueryRun.created_at.desc())
        .limit(5)
        .all()
    )

    failures = []

    for run in etl_failures:
        failures.append({
            "service": "etl",
            "id": run.id,
            "name": run.filename,
            "status": run.status,
            "error_message": run.error_message,
            "created_at": run.created_at,
        })

    for run in rag_failures:
        failures.append({
            "service": "rag",
            "id": run.id,
            "name": run.query,
            "status": run.status,
            "risk_level": run.risk_level,
            "error_message": run.error_message,
            "created_at": run.created_at,
        })

    failures.sort(key=lambda x: x["created_at"], reverse=True)
    return failures[:10]


def get_overview(db: Session):
    etl_summary = get_etl_summary(db)
    rag_summary = get_rag_summary(db)
    recent_failures = get_recent_failures(db)

    return {
        "system_health": {
            "etl_total_runs": etl_summary["total_runs"],
            "etl_failed_runs": etl_summary["failed_runs"],
            "etl_health_score": etl_summary["health_score"],
            "rag_total_queries": rag_summary["total_queries"],
            "rag_failed_queries": rag_summary["failed_queries"],
            "rag_health_score": rag_summary["health_score"],
            "rag_high_risk_queries": rag_summary["high_risk_queries"],
        },
        "etl_summary": etl_summary,
        "rag_summary": rag_summary,
        "recent_failures": recent_failures,
    }