from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db import Base

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    total_rows = Column(Integer, nullable=True)
    total_columns = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    anomalies = Column(Text, nullable=True)
    profile = Column(Text, nullable=True)
    quality_score = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)