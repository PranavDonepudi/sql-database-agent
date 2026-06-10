import sqlite3
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/chinook.db")
MAX_ROWS = 200


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_schema() -> str:
    """Return a compact schema string: table(col type, ...) per line."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    conn.close()

    lines = []
    for table in tables:
        name, ddl = table["name"], table["sql"]
        if not ddl:
            continue
        # Extract column definitions compactly
        conn2 = get_connection()
        cols = conn2.execute(f"PRAGMA table_info({name})").fetchall()
        conn2.close()
        col_parts = [f"{c['name']} {c['type']}" for c in cols]
        lines.append(f"{name}({', '.join(col_parts)})")

    return "\n".join(lines)


def run_query(sql: str) -> dict[str, Any]:
    """Execute a SELECT query safely and return rows + columns."""
    sql = sql.strip().rstrip(";")

    # Safety: only allow SELECT
    first_word = sql.split()[0].upper()
    if first_word != "SELECT":
        return {"error": "Only SELECT queries are allowed.", "rows": [], "columns": []}

    try:
        conn = get_connection()
        conn.execute("PRAGMA query_only = ON")
        # Only append LIMIT if the query doesn't already have one
        if "limit" not in sql.lower():
            sql = sql + f" LIMIT {MAX_ROWS}"
        cursor = conn.execute(sql)
        columns = [d[0] for d in cursor.description]
        rows = [list(row) for row in cursor.fetchall()]
        conn.close()
        return {"columns": columns, "rows": rows, "error": None}
    except Exception as e:
        return {"error": str(e), "rows": [], "columns": []}
