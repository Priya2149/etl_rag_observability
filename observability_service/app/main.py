from fastapi import FastAPI
from app.routes.observability import router as observability_router

app = FastAPI(title="Observability Service")

app.include_router(observability_router)

@app.get("/")
def root():
    return {"message": "Observability Service Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}