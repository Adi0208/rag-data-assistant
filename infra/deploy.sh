#!/bin/bash
# ── deploy.sh ─────────────────────────────────────────────────
# One-command deployment to Google Cloud Run
#
# Usage:
#   chmod +x infra/deploy.sh
#   ./infra/deploy.sh

set -e  # Exit on any error

# ── Config ────────────────────────────────────────────────────
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="rag-data-assistant"
REGION="us-central1"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║       RAG Data Assistant — Cloud Run Deploy      ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║  Project : ${PROJECT_ID}"
echo "║  Service : ${SERVICE_NAME}"
echo "║  Region  : ${REGION}"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Enable required APIs ─────────────────────────────
echo "▶ Step 1/6: Enabling required GCP APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  bigquery.googleapis.com \
  containerregistry.googleapis.com \
  --quiet
echo "  ✅ APIs enabled"

# ── Step 2: Store secrets in Secret Manager ───────────────────
echo ""
echo "▶ Step 2/6: Storing secrets in Secret Manager..."

# Load from local .env
source .env

# Store GEMINI_API_KEY
if gcloud secrets describe GEMINI_API_KEY --quiet 2>/dev/null; then
  echo "  ℹ️  GEMINI_API_KEY secret already exists, updating..."
  echo -n "${GEMINI_API_KEY}" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
else
  echo -n "${GEMINI_API_KEY}" | gcloud secrets create GEMINI_API_KEY --data-file=- --replication-policy=automatic
fi

# Store GCP_PROJECT_ID
if gcloud secrets describe GCP_PROJECT_ID --quiet 2>/dev/null; then
  echo "  ℹ️  GCP_PROJECT_ID secret already exists, updating..."
  echo -n "${GCP_PROJECT_ID}" | gcloud secrets versions add GCP_PROJECT_ID --data-file=-
else
  echo -n "${GCP_PROJECT_ID}" | gcloud secrets create GCP_PROJECT_ID --data-file=- --replication-policy=automatic
fi

echo "  ✅ Secrets stored in Secret Manager (not in code!)"

# ── Step 3: Build Docker image ────────────────────────────────
echo ""
echo "▶ Step 3/6: Building Docker image..."
docker build -f infra/Dockerfile -t "${IMAGE}:latest" .
echo "  ✅ Docker image built"

# ── Step 4: Push to Container Registry ───────────────────────
echo ""
echo "▶ Step 4/6: Pushing image to Container Registry..."
gcloud auth configure-docker --quiet
docker push "${IMAGE}:latest"
echo "  ✅ Image pushed"

# ── Step 5: Deploy to Cloud Run ───────────────────────────────
echo ""
echo "▶ Step 5/6: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image="${IMAGE}:latest" \
  --region=${REGION} \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=3 \
  --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest,GCP_PROJECT_ID=GCP_PROJECT_ID:latest" \
  --set-env-vars="BIGQUERY_DATASET=ecommerce,APP_ENV=production" \
  --quiet
echo "  ✅ Deployed to Cloud Run"

# ── Step 6: Get live URL ──────────────────────────────────────
echo ""
echo "▶ Step 6/6: Fetching live URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region=${REGION} \
  --format='value(status.url)')

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║           🎉 DEPLOYMENT SUCCESSFUL!              ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║"
echo "║  🌐 Live URL: ${SERVICE_URL}"
echo "║"
echo "║  📖 API Docs: ${SERVICE_URL}/docs"
echo "║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Add this URL to your portfolio and resume!"
