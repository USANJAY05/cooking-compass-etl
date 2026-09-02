import sqlite3
from pathlib import Path
from .config import DATABASE_PATH


def get_connection():
    if not Path(DATABASE_PATH).exists():
        raise FileNotFoundError(f"SQLite database not found: {DATABASE_PATH}")
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_ingredients():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, name FROM ingredients ORDER BY id").fetchall()
    return [dict(row) for row in rows]


def get_ingredient(ingredient_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name FROM ingredients WHERE id = ?", (ingredient_id,)
        ).fetchone()
    return dict(row) if row else None
