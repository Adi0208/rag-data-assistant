"""
gemini_sql.py
The AI brain of the RAG Data Assistant.

Flow:
    User Question (plain English)
        → Gemini converts to SQL
        → BigQuery runs the SQL
        → Gemini explains the result in plain English
        → Answer returned to user

Usage (standalone test):
    python backend/gemini_sql.py
"""

import os
import time
from dotenv import load_dotenv
from google.cloud import bigquery
import google.generativeai as genai

load_dotenv()

# ── Config ────────────────────────────────────────────────────
PROJECT_ID  = os.getenv("GCP_PROJECT_ID", "rag-data-assistant")
DATASET_ID  = os.getenv("BIGQUERY_DATASET", "ecommerce")
GEMINI_KEY  = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")


# ── Schema Context (tells Gemini what tables exist) ───────────
SCHEMA_CONTEXT = """
You are a BigQuery SQL expert. The database has these tables in dataset `ecommerce`:

TABLE: ecommerce.customers
  - customer_id    STRING   (e.g. CUST-A1B2C3)
  - first_name     STRING
  - last_name      STRING
  - email          STRING
  - city           STRING   (Mumbai, Delhi, Bangalore, etc.)
  - country        STRING   (India)
  - signup_date    DATE
  - segment        STRING   (Premium, Regular, At-Risk)
  - lifetime_value FLOAT    (total spend potential)

TABLE: ecommerce.products
  - product_id     STRING
  - product_name   STRING   (Smartphone, Laptop, T-Shirt, etc.)
  - category       STRING   (Electronics, Clothing, Home, Sports)
  - subcategory    STRING
  - unit_price     FLOAT
  - cost_price     FLOAT
  - stock_quantity INTEGER
  - supplier       STRING

TABLE: ecommerce.orders
  - order_id          STRING
  - customer_id       STRING   (joins to customers.customer_id)
  - order_date        DATE
  - status            STRING   (Completed, Returned, Cancelled, Pending)
  - total_amount      FLOAT
  - discount_applied  FLOAT
  - shipping_city     STRING
  - shipping_country  STRING
  - payment_method    STRING   (Credit Card, UPI, Net Banking, Wallet)

TABLE: ecommerce.order_items
  - item_id      STRING
  - order_id     STRING   (joins to orders.order_id)
  - product_id   STRING   (joins to products.product_id)
  - quantity     INTEGER
  - unit_price   FLOAT
  - total_price  FLOAT

TABLE: ecommerce.reviews
  - review_id     STRING
  - product_id    STRING   (joins to products.product_id)
  - customer_id   STRING   (joins to customers.customer_id)
  - rating        INTEGER  (1 to 5)
  - review_text   STRING
  - review_date   DATE
  - helpful_votes INTEGER

RULES:
- Always use fully qualified table names: `ecommerce.tablename`
- For revenue questions, use order_items.total_price (not orders.total_amount)
- For completed sales only, filter: orders.status = 'Completed'
- Dates are in DATE format, use DATE() or string comparison
- Always add LIMIT 20 unless user asks for all records
- Return ONLY the SQL query, no explanation, no markdown, no backticks
"""


# ── Step 1: Convert question to SQL ──────────────────────────
def question_to_sql(question: str) -> str:
    """Uses Gemini to convert a natural language question into BigQuery SQL."""

    prompt = f"""
{SCHEMA_CONTEXT}

User question: {question}

Write a BigQuery SQL query to answer this question.
Return ONLY the SQL. No explanation. No markdown formatting. No backticks.
"""

    response = model.generate_content(prompt)
    sql = response.text.strip()

    # Clean up in case Gemini adds markdown anyway
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql


# ── Step 2: Run SQL on BigQuery ───────────────────────────────
def run_sql(sql: str) -> list[dict]:
    """Executes SQL on BigQuery and returns results as a list of dicts."""

    client = bigquery.Client(project=PROJECT_ID)

    try:
        query_job = client.query(sql)
        results   = query_job.result()
        rows      = [dict(row) for row in results]
        return rows
    except Exception as e:
        raise ValueError(f"BigQuery error: {str(e)}\n\nSQL attempted:\n{sql}")


# ── Step 3: Convert results to plain English ──────────────────
def results_to_answer(question: str, sql: str, rows: list[dict]) -> str:
    """Uses Gemini to explain raw query results in plain English."""

    if not rows:
        return "No data found for your question. The query returned zero results."

    # Limit rows sent to Gemini to avoid token limits
    sample = rows[:10]

    prompt = f"""
The user asked: "{question}"

We ran this SQL query:
{sql}

The query returned these results:
{sample}

Total rows returned: {len(rows)}

Please answer the user's question in clear, friendly, business-friendly language.
- Lead with the key insight or answer directly
- Mention specific numbers and names from the results
- Keep it concise (3-5 sentences max)
- Do NOT mention SQL, BigQuery, or technical details
- Write as if you are a helpful data analyst explaining to a business manager
"""

    response = model.generate_content(prompt)
    return response.text.strip()


# ── Main Pipeline: Question → Answer ─────────────────────────
def ask(question: str) -> dict:
    """
    Full pipeline: natural language question → answer.

    Returns:
        {
            "question": str,
            "sql":      str,
            "rows":     list[dict],
            "answer":   str,
            "row_count": int
        }
    """
    print(f"\n🤔 Question: {question}")

    # Step 1: NL → SQL
    print("⚙️  Generating SQL...")
    sql = question_to_sql(question)
    print(f"📝 SQL:\n{sql}\n")

    # Step 2: Run SQL
    print("🔍 Running query on BigQuery...")
    rows = run_sql(sql)
    print(f"✅ {len(rows)} rows returned")
    time.sleep(2) 

    # Step 3: Results → Answer
    print("💬 Generating answer...")
    answer = results_to_answer(question, sql, rows)
    print(f"\n💡 Answer:\n{answer}")

    return {
        "question":  question,
        "sql":       sql,
        "rows":      rows,
        "answer":    answer,
        "row_count": len(rows),
    }


# ── Test it directly ──────────────────────────────────────────
if __name__ == "__main__":
    test_questions = [
        "What are the top 5 product categories by total revenue?",
        "Which city has the most customers?",
        "What is the average order value for Premium customers?",
        "Which payment method is most popular?",
        "What are the top 3 products with the highest return rate?",
    ]

    print("=" * 60)
    print("  RAG Data Assistant — Gemini SQL Engine Test")
    print("=" * 60)

    for q in test_questions:
        print("\n" + "─" * 60)
        result = ask(q)
        print("─" * 60)
