from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from app.db import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    total_rows = Column(Integer)
    total_columns = Column(Integer)
    status = Column(String)
    anomalies = Column(Text)
    profile = Column(Text)
    quality_score = Column(Integer)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class RagDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    status = Column(String)
    created_at = Column(DateTime)


class RagQueryRun(Base):
    __tablename__ = "rag_query_runs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text)
    answer = Column(Text)
    retrieved_chunks = Column(Text)

    sources = Column(Text)
    chunks_used = Column(Integer)
    processing_time_ms = Column(Integer)

    retrieved_count = Column(Integer)
    source_files = Column(Text)
    best_distance = Column(Float)
    risk_level = Column(String)
    evaluation_status = Column(String)
    warning_flags = Column(Text)

    status = Column(String)
    error_message = Column(Text)
    created_at = Column(DateTime)