import sqlite3
import pandas as pd
from contextlib import contextmanager

DB_PATH = "inventory.db"

@contextmanager
def get_db_connection():
    """Context manager for thread-safe SQLite transactions."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initializes the inventory and audit ledger tables if they do not exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit_price REAL NOT NULL DEFAULT 0.0
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                change_qty INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

def fetch_products_dataframe() -> pd.DataFrame:
    """Retrieves all current products for the UI table."""
    with get_db_connection() as conn:
        return pd.read_sql_query(
            "SELECT name AS Product, quantity AS Stock, unit_price AS Price FROM products ORDER BY name ASC",
            conn
        )

def fetch_recent_transactions_dataframe(limit: int = 8) -> pd.DataFrame:
    """Retrieves recent inventory ledger transactions."""
    with get_db_connection() as conn:
        return pd.read_sql_query(
            f"SELECT product_name AS Product, change_qty AS Change, action AS Type, timestamp AS Time "
            f"FROM transactions ORDER BY id DESC LIMIT {limit}",
            conn
        )