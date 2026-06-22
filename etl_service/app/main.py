from fastapi import FastAPI
from app.routes import upload
from app.db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ETL Service")

app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "ETL Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}