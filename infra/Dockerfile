# ── Dockerfile ───────────────────────────────────────────────
# Production container for RAG Data Assistant
# Deployed on Google Cloud Run

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create directories needed at runtime
RUN mkdir -p data/uploads backend/vector_store

# Cloud Run uses PORT env variable (default 8080)
ENV PORT=8080
ENV APP_ENV=production

# Run the app
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
