from fastapi import FastAPI

from app.db import Base, engine
from app.routes import workflow

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agent Service")

app.include_router(workflow.router)


@app.get("/")
def root():
    return {"message": "Agent Service Running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}