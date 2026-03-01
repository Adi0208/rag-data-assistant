"""
rag_engine.py
RAG (Retrieval Augmented Generation) Pipeline.

Flow:
    PDF Upload
        → Extract text
        → Split into chunks
        → Embed each chunk using Gemini
        → Store in local FAISS vector store
        → User asks question
        → Embed question
        → Find most similar chunks
        → Send chunks + question to Gemini
        → Return plain English answer

Usage (standalone test):
    python backend/rag_engine.py

Prerequisites:
    pip install pypdf faiss-cpu numpy
"""

import os
import json
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()

# ── Config ────────────────────────────────────────────────────
GEMINI_KEY       = os.getenv("GEMINI_API_KEY")
VECTOR_STORE_DIR = Path(__file__).parent / "vector_store"
CHUNK_SIZE       = 500    # characters per chunk
CHUNK_OVERLAP    = 50     # overlap between chunks
TOP_K            = 3      # number of chunks to retrieve

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")  # update if needed

# Create vector store directory
VECTOR_STORE_DIR.mkdir(exist_ok=True)


# ── Step 1: Extract text from PDF ────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("Run: pip install pypdf")

    reader = PdfReader(pdf_path)
    text   = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    print(f"  📄 Extracted {len(text)} characters from {Path(pdf_path).name}")
    return text


# ── Step 2: Split text into chunks ───────────────────────────
def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE,
                      overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Splits text into overlapping chunks for better context retrieval."""
    chunks = []
    start  = 0

    while start < len(text):
        end   = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap  # overlap ensures context isn't lost at boundaries

    print(f"  ✂️  Split into {len(chunks)} chunks")
    return chunks


# ── Step 3: Embed chunks using Gemini ────────────────────────
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Converts text chunks into vector embeddings using Gemini."""
    embeddings = []

    for i, text in enumerate(texts):
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_document",
        )
        embeddings.append(result["embedding"])
        time.sleep(1)

        # Progress indicator for large PDFs
        if (i + 1) % 10 == 0:
            print(f"  🔢 Embedded {i + 1}/{len(texts)} chunks...")

    print(f"  ✅ All {len(texts)} chunks embedded")
    return embeddings


# ── Step 4: Save to local vector store ───────────────────────
def save_vector_store(doc_name: str, chunks: list[str],
                      embeddings: list[list[float]]) -> None:
    """Saves chunks and their embeddings to local JSON files."""
    store_path = VECTOR_STORE_DIR / f"{doc_name}.json"

    data = {
        "doc_name":   doc_name,
        "chunks":     chunks,
        "embeddings": embeddings,
    }

    with open(store_path, "w") as f:
        json.dump(data, f)

    print(f"  💾 Vector store saved: {store_path}")


# ── Step 5: Load vector store ────────────────────────────────
def load_vector_store(doc_name: str) -> dict | None:
    """Loads a saved vector store by document name."""
    store_path = VECTOR_STORE_DIR / f"{doc_name}.json"

    if not store_path.exists():
        return None

    with open(store_path, "r") as f:
        return json.load(f)


def list_documents() -> list[str]:
    """Returns list of all ingested document names."""
    return [f.stem for f in VECTOR_STORE_DIR.glob("*.json")]


# ── Step 6: Find most relevant chunks ────────────────────────
def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculates cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def retrieve_relevant_chunks(question: str, doc_name: str,
                              top_k: int = TOP_K) -> list[str]:
    """Finds the most relevant chunks for a given question."""

    # Load the vector store
    store = load_vector_store(doc_name)
    if not store:
        raise ValueError(f"Document '{doc_name}' not found. Please ingest it first.")

    # Embed the question
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=question,
        task_type="retrieval_query",
    )
    question_embedding = result["embedding"]

    # Calculate similarity with all chunks
    similarities = []
    for i, chunk_embedding in enumerate(store["embeddings"]):
        score = cosine_similarity(question_embedding, chunk_embedding)
        similarities.append((score, i, store["chunks"][i]))

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[0], reverse=True)

    # Return top K chunks
    top_chunks = [chunk for _, _, chunk in similarities[:top_k]]
    print(f"  🎯 Retrieved top {len(top_chunks)} relevant chunks")
    return top_chunks


# ── Step 7: Generate answer from chunks ──────────────────────
def answer_from_chunks(question: str, chunks: list[str],
                       doc_name: str) -> str:
    """Uses Gemini to answer a question based on retrieved chunks."""

    context = "\n\n---\n\n".join(chunks)

    prompt = f"""
You are a helpful assistant answering questions about a document called "{doc_name}".

Here are the most relevant sections from the document:

{context}

---

User question: {question}

Instructions:
- Answer based ONLY on the context provided above
- If the answer is not in the context, say "I couldn't find that information in the document"
- Be concise and clear
- Do not make up information
- Quote specific parts of the document when relevant
"""

    response = model.generate_content(prompt)
    return response.text.strip()


# ── Full Pipeline: Ingest PDF ─────────────────────────────────
def ingest_pdf(pdf_path: str) -> dict:
    """
    Full ingestion pipeline for a PDF file.

    Steps: Extract → Chunk → Embed → Save
    Returns summary of what was ingested.
    """
    pdf_path = Path(pdf_path)
    doc_name = pdf_path.stem  # filename without extension

    print(f"\n📥 Ingesting: {pdf_path.name}")

    # Extract text
    text = extract_text_from_pdf(str(pdf_path))

    if not text.strip():
        raise ValueError("Could not extract any text from the PDF.")

    # Split into chunks
    chunks = split_into_chunks(text)

    # Embed chunks
    print(f"  🔢 Embedding {len(chunks)} chunks (this may take a moment)...")
    embeddings = embed_texts(chunks)

    # Save vector store
    save_vector_store(doc_name, chunks, embeddings)

    return {
        "doc_name":    doc_name,
        "pages":       text.count("\n\n"),
        "chunks":      len(chunks),
        "characters":  len(text),
    }


# ── Full Pipeline: Ask Question ───────────────────────────────
def ask_document(question: str, doc_name: str) -> dict:
    """
    Full RAG pipeline: question → relevant chunks → answer.

    Returns:
        {
            "question": str,
            "doc_name": str,
            "chunks":   list[str],
            "answer":   str,
        }
    """
    print(f"\n🤔 Question: {question}")
    print(f"📄 Document: {doc_name}")

    # Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(question, doc_name)

    # Generate answer
    print("  💬 Generating answer...")
    answer = answer_from_chunks(question, chunks, doc_name)

    print(f"\n💡 Answer:\n{answer}")

    return {
        "question": question,
        "doc_name": doc_name,
        "chunks":   chunks,
        "answer":   answer,
    }


# ── Test it directly ──────────────────────────────────────────
if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("  RAG Engine — PDF Q&A Test")
    print("=" * 60)

    # Check if a PDF path was provided as argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Create a sample text file to test with (no PDF needed)
        sample_path = Path(__file__).parent.parent / "data" / "sample_report.txt"
        sample_path.write_text("""
E-Commerce Business Report — Q4 2024

Executive Summary:
Our e-commerce platform had a strong Q4 2024 with total revenue of Rs 45.2 crore,
representing a 23% growth over Q3 2024. Electronics remained the top category
contributing 42% of total revenue.

Return Policy:
Customers may return products within 30 days of delivery for a full refund.
Electronics have a 15-day return window. Items must be in original packaging.
Damaged or used items are not eligible for return.

Customer Segments:
Premium customers account for 20% of our user base but contribute 58% of revenue.
Regular customers make up 60% of users with 35% revenue contribution.
At-Risk customers need re-engagement campaigns to prevent churn.

Top Performing Products:
1. Smartphones - Rs 12.1 crore
2. Laptops - Rs 8.4 crore
3. Headphones - Rs 4.2 crore

Challenges:
The return rate for Electronics increased to 8.2% in Q4, up from 6.1% in Q3.
This is primarily driven by Smartphone returns due to software issues.
        """)
        print(f"\n📝 No PDF provided. Using sample report for testing.")
        print(f"   (In production, pass a real PDF path as argument)\n")

        # Ingest the sample file as if it were a PDF
        doc_name = "sample_report"
        text     = sample_path.read_text()
        chunks   = split_into_chunks(text)
        print(f"  🔢 Embedding {len(chunks)} chunks...")
        embeddings = embed_texts(chunks)
        save_vector_store(doc_name, chunks, embeddings)
        print(f"  ✅ Sample report ingested!\n")

        # Test questions
        test_questions = [
            "What is the return policy?",
            "Which product category had the highest revenue?",
            "What challenges did the business face in Q4?",
        ]

        print("─" * 60)
        for q in test_questions:
            result = ask_document(q, doc_name)
            print("─" * 60)
