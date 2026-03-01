# 🤖 RAG-Powered Data Assistant on GCP

> **Ask your data warehouse in plain English.** Powered by Gemini AI + BigQuery + LangChain — deployed on Google Cloud Run.

![Architecture](https://img.shields.io/badge/GCP-BigQuery-blue) ![Gemini](https://img.shields.io/badge/AI-Gemini_Pro-orange) ![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green) ![Cloud Run](https://img.shields.io/badge/Deploy-Cloud_Run-blue)

---

## 🎯 What This Does

This project turns your BigQuery data warehouse into a **conversational AI assistant**. Instead of writing SQL, anyone on your team can ask:

- *"What were the top 5 selling product categories last quarter?"*
- *"Which customer segment has the highest return rate?"*
- *"Show me monthly revenue trends for 2024"*
- *"What does our return policy say?"* ← answered from uploaded PDFs

The assistant handles **two types of queries**:
- **Structured** → Natural Language → SQL → BigQuery → Plain English answer
- **Unstructured** → Question → Vector Search → PDF chunks → Gemini → Answer

---

## 🏗️ Architecture

```
User (Chat UI)
      │
      ▼
FastAPI Backend (Cloud Run)
      │
      ├── gemini_sql.py   →  NL → SQL → BigQuery → Answer
      │
      └── rag_engine.py   →  PDF chunks → Embeddings → Vector Search → Answer
                                                              │
                                              ┌──────────────┴──────────────┐
                                         BigQuery                    Vector Store
                                      (Structured Data)          (PDF Documents)
                                              │                           │
                                              └──────────┬────────────────┘
                                                         │
                                                    Gemini API
                                              (Text + Embeddings)
```

---

## 📁 Project Structure

```
rag-data-assistant/
│
├── bigquery/
│   ├── schema.sql            # Table definitions
│   ├── generate_data.py      # Generates realistic sample data
│   ├── load_to_bigquery.py   # Uploads CSVs to BigQuery
│   └── sample_queries.sql    # Test queries to verify data
│
├── backend/
│   ├── main.py               # FastAPI app + routes         [Phase 4]
│   ├── gemini_sql.py         # NL → SQL → Answer engine     [Phase 2]
│   └── rag_engine.py         # PDF RAG pipeline             [Phase 3]
│
├── frontend/
│   └── index.html            # Chat UI                      [Phase 5]
│
├── infra/
│   ├── Dockerfile            # Container config             [Phase 6]
│   └── cloudbuild.yaml       # CI/CD to Cloud Run           [Phase 6]
│
├── data/                     # Generated CSV files (gitignored)
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Google Cloud account (free tier works!)
- `gcloud` CLI installed

### Step 1 — Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/rag-data-assistant.git
cd rag-data-assistant

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Configure Environment
```bash
cp .env.example .env
# Edit .env with your GCP Project ID and Gemini API Key
```

Get your **Gemini API Key** free at: https://aistudio.google.com/app/apikey

### Step 3 — Authenticate with GCP
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Step 4 — Generate & Load Sample Data
```bash
# Generate CSV files
python bigquery/generate_data.py

# Upload to BigQuery
python bigquery/load_to_bigquery.py
```

### Step 5 — Verify Data in BigQuery
Open `bigquery/sample_queries.sql` in the BigQuery Console and run a few queries to confirm everything loaded correctly.

### Step 6 — Run the App (Phase 4 onwards)
```bash
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

---

## 📊 Dataset Overview

The app uses a realistic **Indian E-Commerce** dataset:

| Table | Rows | Description |
|-------|------|-------------|
| customers | 500 | Customer profiles with segments |
| products | 80 | Products across 4 categories |
| orders | 2,000 | Orders from 2022–2024 |
| order_items | ~5,000 | Line items per order |
| reviews | 800 | Product ratings & text |

**Sample questions the AI can answer:**
- Revenue by category, city, or time period
- Top/bottom performing products
- Customer segment behavior
- Return rates & order status breakdowns
- Payment method distribution

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI / LLM | Google Gemini Pro |
| Embeddings | Gemini Embedding Model |
| Data Warehouse | Google BigQuery |
| Vector Store | FAISS (local) → AlloyDB (production) |
| Backend | Python FastAPI |
| Orchestration | LangChain |
| Deployment | Google Cloud Run |
| CI/CD | Cloud Build |

---

## 🔮 Roadmap

- [x] Phase 1 — Dataset + BigQuery setup
- [ ] Phase 2 — Gemini NL→SQL engine
- [ ] Phase 3 — PDF RAG pipeline
- [ ] Phase 4 — FastAPI backend
- [ ] Phase 5 — Chat UI
- [ ] Phase 6 — Cloud Run deployment

---

## 👨‍💻 Author

**Aditya Kumar Gautam** — Cloud Data Engineer | GCP | AI-Ready Architectures

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/aditya-kumar-gautam-421a09185/)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-green)](https://adi0208.github.io/AdityaPortfolio/)

---

*Built to showcase modern AI-era data engineering on Google Cloud Platform.*
