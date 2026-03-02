# 🤖 RAG-Powered Data Assistant on GCP

> **Ask your data warehouse in plain English.** Powered by Gemini AI + BigQuery + RAG pipelines — deployed live on Google Cloud Run.

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Available-00e5ff?style=for-the-badge)](https://rag-data-assistant-2pre7ugmmq-uc.a.run.app)
[![GitHub](https://img.shields.io/badge/GitHub-Adi0208-181717?style=for-the-badge&logo=github)](https://github.com/Adi0208/rag-data-assistant)
[![GCP](https://img.shields.io/badge/GCP-BigQuery-4285F4?style=for-the-badge&logo=google-cloud)](https://cloud.google.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini-orange?style=for-the-badge)](https://ai.google.dev)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge)](https://fastapi.tiangolo.com)
[![Cloud Run](https://img.shields.io/badge/Deploy-Cloud_Run-4285F4?style=for-the-badge)](https://cloud.google.com/run)

---

## 🌐 Live Demo

**Try it now → [https://rag-data-assistant-2pre7ugmmq-uc.a.run.app](https://rag-data-assistant-2pre7ugmmq-uc.a.run.app)**

No setup required. Just open and ask a question like:
- *"What are the top 5 product categories by total revenue?"*
- *"Which city has the most customers?"*
- *"What is the return rate for Electronics?"*

---

## 🎯 What This Project Does

This project turns a BigQuery data warehouse into a **conversational AI assistant**. Instead of writing SQL, anyone can ask business questions in plain English and get instant, accurate answers — powered by Google Gemini AI.

It handles **two types of queries:**

| Query Type | How it works |
|-----------|-------------|
| 📊 **Data Questions** | Plain English → Gemini generates SQL → BigQuery executes → Gemini explains results |
| 📄 **Document Questions** | PDF uploaded → chunked → embedded → vector search → Gemini answers from context |

---

## 🏗️ Architecture

```
User (Chat UI — Dark/Light Theme)
         │
         ▼
  FastAPI Backend (Google Cloud Run)
         │
         ├── gemini_sql.py   →  NL → SQL → BigQuery → Plain English Answer
         │
         └── rag_engine.py   →  PDF → Chunks → Embeddings → Vector Search → Answer
                                                    │                   │
                                          ┌─────────┴───────┐   ┌──────┴──────┐
                                       BigQuery          Vector Store
                                    (Structured Data)   (PDF Documents)
                                          │                   │
                                          └────────┬──────────┘
                                                   │
                                            Gemini API
                                     (Text Generation + Embeddings)
                                                   │
                                         GCP Secret Manager
                                          (API Key Storage)
```

---

## ✨ Key Features

- 🧠 **Natural Language to SQL** — Gemini converts plain English questions to BigQuery SQL automatically
- 📄 **PDF RAG Pipeline** — Upload any PDF and ask questions about its contents
- 🔍 **Transparent AI** — Every answer shows the generated SQL so users can verify accuracy
- 🌙 **Dark / Light Theme** — Toggle between themes for comfortable viewing
- 📊 **Data Tables** — Query results displayed as formatted tables with Indian number formatting
- 🔐 **Production Security** — API keys stored in GCP Secret Manager, never in code
- ☁️ **Serverless Deployment** — Runs on Google Cloud Run, scales to zero when not in use
- ⚡ **Real-time** — Answers returned in seconds with typing indicators

---

## 📊 Dataset

The assistant queries a realistic **Indian E-Commerce** dataset loaded in BigQuery:

| Table | Rows | Description |
|-------|------|-------------|
| `customers` | 500 | Profiles with city, segment, lifetime value |
| `products` | 80 | Products across Electronics, Clothing, Home, Sports |
| `orders` | 2,000 | Orders from 2022–2024 with status and payment method |
| `order_items` | ~6,000 | Line items per order with quantities and prices |
| `reviews` | 800 | Product ratings and review text |

**Sample questions you can ask:**
- Revenue by category, city, or time period
- Top/bottom performing products
- Customer segment behavior analysis
- Return rates and order status breakdowns
- Payment method distribution
- Monthly revenue trends

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| AI / LLM | Google Gemini | NL→SQL generation + answer explanation |
| Embeddings | Gemini Embedding Model | PDF chunk vectorization |
| Data Warehouse | Google BigQuery | Structured data storage and querying |
| Vector Store | FAISS | Local vector similarity search |
| Backend | Python FastAPI | REST API connecting all components |
| Orchestration | LangChain | AI pipeline management |
| Deployment | Google Cloud Run | Serverless container hosting |
| Secrets | GCP Secret Manager | Secure API key storage |
| Container | Docker | Application containerization |
| CI/CD | Cloud Build | Automated deployment pipeline |

---

## 📁 Project Structure

```
rag-data-assistant/
│
├── backend/
│   ├── main.py           # FastAPI app + all API endpoints
│   ├── gemini_sql.py     # NL → SQL → BigQuery → Answer engine
│   ├── rag_engine.py     # PDF RAG pipeline (chunk → embed → search)
│   └── secrets.py        # GCP Secret Manager integration
│
├── bigquery/
│   ├── schema.sql        # BigQuery table definitions
│   ├── generate_data.py  # Realistic sample data generator
│   ├── load_to_bigquery.py # Data loader script
│   └── sample_queries.sql  # Verification queries
│
├── frontend/
│   └── index.html        # Chat UI (dark/light theme, data tables)
│
├── infra/
│   ├── Dockerfile        # Container configuration
│   ├── cloudbuild.yaml   # CI/CD pipeline
│   └── deploy.sh         # One-command deployment script
│
├── data/                 # Generated CSV files (gitignored)
├── .env.example          # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Google Cloud account
- Gemini API Key (free at [aistudio.google.com](https://aistudio.google.com/app/apikey))

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Adi0208/rag-data-assistant.git
cd rag-data-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your GCP Project ID and Gemini API Key

# 5. Authenticate with GCP
gcloud auth application-default login

# 6. Generate and load sample data
python bigquery/generate_data.py
python bigquery/load_to_bigquery.py

# 7. Start the server
uvicorn backend.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

---

## ☁️ Deploy to Cloud Run

```bash
# 1. Store API key in Secret Manager
echo -n "your-gemini-api-key" | gcloud secrets create GEMINI_API_KEY --data-file=-

# 2. Build and push Docker image
docker build -f infra/Dockerfile -t gcr.io/YOUR_PROJECT/rag-data-assistant:latest .
docker push gcr.io/YOUR_PROJECT/rag-data-assistant:latest

# 3. Deploy to Cloud Run
gcloud run deploy rag-data-assistant \
  --image=gcr.io/YOUR_PROJECT/rag-data-assistant:latest \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --set-env-vars=GCP_PROJECT_ID=YOUR_PROJECT,BIGQUERY_DATASET=ecommerce
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/ask-data` | Ask a data question (NL→SQL→Answer) |
| `POST` | `/api/upload-pdf` | Upload and ingest a PDF |
| `POST` | `/api/ask-doc` | Ask a question about a PDF |
| `GET` | `/api/documents` | List ingested documents |
| `GET` | `/api/sample-questions` | Get sample questions |
| `GET` | `/docs` | Interactive API documentation |

---

## 👨‍💻 Author

**Aditya Kumar Gautam** — Cloud Data Engineer | GCP | AI-Ready Architectures

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/aditya-kumar-gautam-421a09185/)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-00e5ff?style=for-the-badge)](https://adi0208.github.io/AdityaPortfolio/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/Adi0208)

---

*Built to demonstrate production-grade AI data engineering on Google Cloud Platform — RAG pipelines, NL→SQL generation, Secret Manager integration, and serverless deployment.*
