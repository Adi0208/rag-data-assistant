"""
secrets.py
Reads secrets from GCP Secret Manager in production,
falls back to .env file in development.

This is the production-grade way to handle API keys —
secrets never touch your code or GitHub.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_secret(secret_name: str) -> str:
    """
    Gets a secret value.
    - In production (Cloud Run): reads from GCP Secret Manager
    - In development (local):    reads from .env file
    """
    env = os.getenv("APP_ENV", "development")

    # Development — use .env file
    if env == "development":
        value = os.getenv(secret_name)
        if not value:
            raise ValueError(f"Missing env variable: {secret_name}. Add it to your .env file.")
        return value

    # Production — use Secret Manager
    # (Secrets are mounted as env vars via Cloud Run --set-secrets flag)
    value = os.getenv(secret_name)
    if not value:
        raise ValueError(f"Missing secret: {secret_name}. Add it to GCP Secret Manager.")
    return value


# ── Pre-load all secrets at startup ──────────────────────────
# This fails fast if any secret is missing
def load_all_secrets() -> dict:
    """Loads and validates all required secrets at app startup."""
    required = ["GEMINI_API_KEY", "GCP_PROJECT_ID", "BIGQUERY_DATASET"]
    secrets  = {}

    print("🔐 Loading secrets...")
    for key in required:
        try:
            secrets[key] = get_secret(key)
            print(f"  ✅ {key} loaded")
        except ValueError as e:
            print(f"  ❌ {e}")
            raise

    print("✅ All secrets loaded successfully\n")
    return secrets
