from fastapi import FastAPI
from app.routes import rag
from app.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG Service")

app.include_router(rag.router)

@app.get("/")
def root():
    return {"message": "RAG Service Running"}