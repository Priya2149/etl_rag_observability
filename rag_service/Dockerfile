FROM python:3.11-slim

WORKDIR /app

COPY rag_service/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        torch==2.12.1 && \
    pip install --no-cache-dir -r requirements.txt

COPY shared ./shared
COPY rag_service/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
