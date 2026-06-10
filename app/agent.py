import re
from app.llm import ask
from app.db import get_schema, run_query

SQL_SYSTEM = """You are an expert SQL assistant. Given a SQLite database schema and a user question,
write a single valid SQLite SELECT query that answers the question.

Rules:
- Output ONLY the raw SQL query — no markdown, no backticks, no explanation.
- Use only tables and columns that exist in the schema.
- Always use LIMIT if the result could be large (default LIMIT 20).
- Use aliases for readability.
- Never use DROP, INSERT, UPDATE, DELETE, or any write operations.
"""

EXPLAIN_SYSTEM = """You are a data analyst assistant. Given a SQL query and its results,
write a clear, concise natural language summary of the findings in 2-4 sentences.
Focus on insights, not on describing the table structure."""

CORRECT_SYSTEM = """You are an expert SQL debugger. A SQL query failed with an error.
Given the schema, the original question, the broken query, and the error message,
output a corrected SQLite SELECT query.
Output ONLY the raw SQL query — no markdown, no backticks, no explanation."""


def _extract_sql(raw: str) -> str:
    """Strip markdown code fences if the model wraps output in them."""
    raw = raw.strip()
    match = re.search(r"```(?:sql)?\s*(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Remove inline backticks
    if raw.startswith("`") and raw.endswith("`"):
        return raw.strip("`").strip()
    return raw


def generate_sql(question: str, schema: str) -> str:
    prompt = f"""Schema:
{schema}

Question: {question}

SQL query:"""
    raw = ask(prompt, SQL_SYSTEM)
    return _extract_sql(raw)


def correct_sql(question: str, schema: str, broken_sql: str, error: str) -> str:
    prompt = f"""Schema:
{schema}

Question: {question}

Broken query:
{broken_sql}

Error:
{error}

Corrected SQL query:"""
    raw = ask(prompt, CORRECT_SYSTEM)
    return _extract_sql(raw)


def explain_results(question: str, sql: str, columns: list, rows: list) -> str:
    sample_rows = rows[:10]
    table_preview = "\t".join(columns) + "\n"
    table_preview += "\n".join("\t".join(str(v) for v in row) for row in sample_rows)
    if len(rows) > 10:
        table_preview += f"\n... ({len(rows)} total rows)"

    prompt = f"""User question: {question}

SQL query used:
{sql}

Query results:
{table_preview}

Summary:"""
    return ask(prompt, EXPLAIN_SYSTEM)


def run_agent(question: str) -> dict:
    schema = get_schema()
    sql = generate_sql(question, schema)

    result = run_query(sql)

    # One self-correction attempt on SQL error
    if result["error"]:
        corrected = correct_sql(question, schema, sql, result["error"])
        result = run_query(corrected)
        used_sql = corrected
    else:
        used_sql = sql

    if result["error"]:
        return {
            "question": question,
            "sql": used_sql,
            "columns": [],
            "rows": [],
            "explanation": f"Could not execute query: {result['error']}",
            "error": result["error"],
        }

    explanation = explain_results(question, used_sql, result["columns"], result["rows"])

    return {
        "question": question,
        "sql": used_sql,
        "columns": result["columns"],
        "rows": result["rows"],
        "explanation": explanation,
        "error": None,
    }
