import os
import shutil
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

UPLOAD_DIR = "app/uploads"
CHROMA_DIR = "app/chroma_store"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def save_uploaded_file(file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

def load_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=80,
        chunk_overlap=20,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)

def ingest_document(file_path: str):
    text = load_text_file(file_path)
    chunks = chunk_text(text)

    metadatas = [{"source": file_path, "chunk_index": i} for i in range(len(chunks))]

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        metadatas=metadatas,
        persist_directory=CHROMA_DIR
    )
    vectorstore.persist()

    return {
        "chunk_count": len(chunks),
        "message": "Document ingested successfully"
    }