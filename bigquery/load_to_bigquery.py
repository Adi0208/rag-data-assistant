"""
load_to_bigquery.py
Uploads generated CSV files to BigQuery.

Prerequisites:
    pip install google-cloud-bigquery pandas pyarrow python-dotenv

Usage:
    1. Set your GCP project ID in .env file
    2. Run: python load_to_bigquery.py

Authentication:
    Make sure you're authenticated:
    gcloud auth application-default login
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery

# Load .env file
load_dotenv()

# ── CONFIG — Update these ─────────────────────────────────────
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
DATASET_ID = "ecommerce"
DATA_DIR   = Path(__file__).parent.parent / "data"

# Table → CSV file mapping
TABLES = [
    "customers",
    "products",
    "orders",
    "order_items",
    "reviews",
]

# BigQuery schema definitions (matches schema.sql)
SCHEMAS = {
    "customers": [
        bigquery.SchemaField("customer_id",    "STRING"),
        bigquery.SchemaField("first_name",     "STRING"),
        bigquery.SchemaField("last_name",      "STRING"),
        bigquery.SchemaField("email",          "STRING"),
        bigquery.SchemaField("city",           "STRING"),
        bigquery.SchemaField("country",        "STRING"),
        bigquery.SchemaField("signup_date",    "DATE"),
        bigquery.SchemaField("segment",        "STRING"),
        bigquery.SchemaField("lifetime_value", "FLOAT"),
    ],
    "products": [
        bigquery.SchemaField("product_id",      "STRING"),
        bigquery.SchemaField("product_name",    "STRING"),
        bigquery.SchemaField("category",        "STRING"),
        bigquery.SchemaField("subcategory",     "STRING"),
        bigquery.SchemaField("unit_price",      "FLOAT"),
        bigquery.SchemaField("cost_price",      "FLOAT"),
        bigquery.SchemaField("stock_quantity",  "INTEGER"),
        bigquery.SchemaField("supplier",        "STRING"),
    ],
    "orders": [
        bigquery.SchemaField("order_id",         "STRING"),
        bigquery.SchemaField("customer_id",      "STRING"),
        bigquery.SchemaField("order_date",       "DATE"),
        bigquery.SchemaField("status",           "STRING"),
        bigquery.SchemaField("total_amount",     "FLOAT"),
        bigquery.SchemaField("discount_applied", "FLOAT"),
        bigquery.SchemaField("shipping_city",    "STRING"),
        bigquery.SchemaField("shipping_country", "STRING"),
        bigquery.SchemaField("payment_method",   "STRING"),
    ],
    "order_items": [
        bigquery.SchemaField("item_id",     "STRING"),
        bigquery.SchemaField("order_id",    "STRING"),
        bigquery.SchemaField("product_id",  "STRING"),
        bigquery.SchemaField("quantity",    "INTEGER"),
        bigquery.SchemaField("unit_price",  "FLOAT"),
        bigquery.SchemaField("total_price", "FLOAT"),
    ],
    "reviews": [
        bigquery.SchemaField("review_id",     "STRING"),
        bigquery.SchemaField("product_id",    "STRING"),
        bigquery.SchemaField("customer_id",   "STRING"),
        bigquery.SchemaField("rating",        "INTEGER"),
        bigquery.SchemaField("review_text",   "STRING"),
        bigquery.SchemaField("review_date",   "DATE"),
        bigquery.SchemaField("helpful_votes", "INTEGER"),
    ],
}


def create_dataset_if_not_exists(client: bigquery.Client) -> None:
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset_ref.location = "US"
    try:
        client.get_dataset(dataset_ref)
        print(f"  Dataset '{DATASET_ID}' already exists.")
    except Exception:
        client.create_dataset(dataset_ref)
        print(f"  ✅ Dataset '{DATASET_ID}' created.")


def load_table(client: bigquery.Client, table_name: str) -> None:
    csv_path = DATA_DIR / f"{table_name}.csv"
    if not csv_path.exists():
        print(f"  ⚠️  {csv_path} not found. Run generate_data.py first.")
        return

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMAS[table_name],
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,          # Skip header row
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite each run
    )

    with open(csv_path, "rb") as f:
        job = client.load_table_from_file(f, table_ref, job_config=job_config)

    job.result()  # Wait for job to complete

    table = client.get_table(table_ref)
    print(f"  ✅ {table_name}: {table.num_rows} rows loaded → {table_ref}")


def main():
    print(f"\n🚀 Starting BigQuery data load")
    print(f"   Project : {PROJECT_ID}")
    print(f"   Dataset : {DATASET_ID}")
    print(f"   Data Dir: {DATA_DIR}\n")

    client = bigquery.Client(project=PROJECT_ID)

    print("Step 1: Ensuring dataset exists...")
    create_dataset_if_not_exists(client)

    print("\nStep 2: Loading tables...")
    for table in TABLES:
        print(f"\n  Loading '{table}'...")
        load_table(client, table)

    print("\n✅ All tables loaded successfully!")
    print(f"\nVerify in BigQuery Console:")
    print(f"https://console.cloud.google.com/bigquery?project={PROJECT_ID}")


if __name__ == "__main__":
    main()