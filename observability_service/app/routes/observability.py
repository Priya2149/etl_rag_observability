from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.summary import (
    get_overview,
    get_etl_summary,
    get_rag_summary,
    get_recent_failures,
)

router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return get_overview(db)


@router.get("/etl-summary")
def etl_summary(db: Session = Depends(get_db)):
    return get_etl_summary(db)


@router.get("/rag-summary")
def rag_summary(db: Session = Depends(get_db)):
    return get_rag_summary(db)


@router.get("/recent-failures")
def recent_failures(db: Session = Depends(get_db)):
    return get_recent_failures(db)