from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from app.db import Base

class RagDocument(Base):
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow)


class RagQueryRun(Base):
    __tablename__ = "rag_query_runs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    retrieved_chunks = Column(Text, nullable=True)
    retrieved_count = Column(Integer, nullable=True)
    source_files = Column(Text, nullable=True)
    best_distance = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    evaluation_status = Column(String, nullable=True)
    warning_flags = Column(Text, nullable=True)
    status = Column(String, default="completed")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)