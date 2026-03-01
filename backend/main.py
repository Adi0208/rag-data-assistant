"""
main.py
FastAPI backend for the RAG Data Assistant.

Connects:
    - gemini_sql.py  → /api/ask-data    (BigQuery questions)
    - rag_engine.py  → /api/ask-doc     (PDF questions)
    - rag_engine.py  → /api/upload-pdf  (PDF ingestion)

Usage:
    uvicorn backend.main:app --reload --port 8000

Then open:
    http://localhost:8000         → Chat UI
    http://localhost:8000/docs    → API docs (auto-generated!)
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── Import our AI engines ─────────────────────────────────────
from backend.gemini_sql import ask as ask_data
from backend.rag_engine  import ingest_pdf, ask_document, list_documents

# ── App Setup ─────────────────────────────────────────────────
app = FastAPI(
    title       = "RAG Data Assistant",
    description = "Ask your BigQuery data warehouse and PDF documents in plain English",
    version     = "1.0.0",
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Upload directory for PDFs
UPLOAD_DIR = Path(__file__).parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Request / Response Models ─────────────────────────────────
class DataQuestion(BaseModel):
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the top 5 product categories by revenue?"
            }
        }


class DocQuestion(BaseModel):
    question: str
    doc_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the return policy?",
                "doc_name": "sample_report"
            }
        }


# ── Health Check ──────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    """Check if the API is running."""
    return {
        "status":  "healthy",
        "message": "RAG Data Assistant is running!",
        "version": "1.0.0",
    }


# ── Endpoint 1: Ask Data (BigQuery + Gemini SQL) ──────────────
@app.post("/api/ask-data")
async def ask_data_endpoint(body: DataQuestion):
    """
    Ask a question about your e-commerce data.
    Converts plain English → SQL → BigQuery → Plain English answer.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = ask_data(body.question)
        return {
            "success":   True,
            "type":      "data",
            "question":  result["question"],
            "answer":    result["answer"],
            "sql":       result["sql"],
            "row_count": result["row_count"],
            "rows":      result["rows"][:5],  # Return first 5 rows as preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Endpoint 2: Upload PDF ────────────────────────────────────
@app.post("/api/upload-pdf")
async def upload_pdf_endpoint(file: UploadFile = File(...)):
    """
    Upload and ingest a PDF document for Q&A.
    Extracts text, chunks it, embeds it, and saves to vector store.
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = ingest_pdf(str(file_path))
        return {
            "success":    True,
            "message":    f"Successfully ingested '{file.filename}'",
            "doc_name":   result["doc_name"],
            "chunks":     result["chunks"],
            "characters": result["characters"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Endpoint 3: Ask Document (RAG) ───────────────────────────
@app.post("/api/ask-doc")
async def ask_doc_endpoint(body: DocQuestion):
    """
    Ask a question about an uploaded PDF document.
    Uses RAG: embeds question → finds relevant chunks → Gemini answers.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    if not body.doc_name.strip():
        raise HTTPException(status_code=400, detail="Document name cannot be empty")

    try:
        result = ask_document(body.question, body.doc_name)
        return {
            "success":  True,
            "type":     "document",
            "question": result["question"],
            "answer":   result["answer"],
            "doc_name": result["doc_name"],
            "chunks":   result["chunks"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Endpoint 4: List Documents ────────────────────────────────
@app.get("/api/documents")
def list_documents_endpoint():
    """Returns list of all ingested PDF documents."""
    docs = list_documents()
    return {
        "success":   True,
        "documents": docs,
        "count":     len(docs),
    }


# ── Endpoint 5: Sample Questions ─────────────────────────────
@app.get("/api/sample-questions")
def sample_questions():
    """Returns sample questions to help users get started."""
    return {
        "data_questions": [
            "What are the top 5 product categories by total revenue?",
            "Which city has the most customers?",
            "What is the average order value for Premium customers?",
            "Which payment method is most popular?",
            "Show me monthly revenue trend for 2024",
            "Which products have the highest return rate?",
            "How many orders were placed in Q4 2024?",
            "What is the total revenue by customer segment?",
        ],
        "doc_questions": [
            "What is the return policy?",
            "What were the key findings?",
            "What challenges were mentioned?",
            "Summarize the executive summary",
        ],
    }


# ── Serve Frontend ────────────────────────────────────────────
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def serve_frontend():
        """Serve the chat UI."""
        html_file = frontend_path / "index.html"
        if html_file.exists():
            return HTMLResponse(content=html_file.read_text())
        return HTMLResponse(content="<h1>Frontend not found</h1>")

else:
    @app.get("/")
    def root():
        return {
            "message": "RAG Data Assistant API is running!",
            "docs":    "Visit /docs for interactive API documentation",
        }


# ── Run directly ──────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
