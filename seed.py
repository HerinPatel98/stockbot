"""
seed.py - Pre-populates the SQLite database with realistic initial inventory
and transaction logs so your dashboard is not empty during the college demo.
"""

import sqlite3

DB_PATH = "inventory.db"

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure tables exist
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

    # Initial sample catalog
    sample_products = [
        ("Mechanical Keyboard", 35, 45.00),
        ("Wireless Mouse", 12, 18.50),
        ("USB-C Hub", 50, 24.00),
        ("27-inch Monitor", 8, 180.00),
        ("Laptop Stand", 22, 19.99),
        ("Noise-Cancelling Headphones", 6, 85.00),
        ("Webcam 1080p", 15, 39.50)
    ]

    # Preload initial restock logs
    sample_transactions = [
        ("Mechanical Keyboard", 35, "RESTOCK"),
        ("Wireless Mouse", 20, "RESTOCK"),
        ("Wireless Mouse", -8, "SALE"),
        ("USB-C Hub", 50, "RESTOCK"),
        ("27-inch Monitor", 10, "RESTOCK"),
        ("27-inch Monitor", -2, "SALE"),
        ("Laptop Stand", 25, "RESTOCK"),
        ("Laptop Stand", -3, "SALE"),
        ("Noise-Cancelling Headphones", 6, "RESTOCK"),
        ("Webcam 1080p", 15, "RESTOCK")
    ]

    # Insert products (ignoring duplicates if already run)
    for name, qty, price in sample_products:
        cursor.execute("""
            INSERT OR REPLACE INTO products (name, quantity, unit_price)
            VALUES (?, ?, ?)
        """, (name, qty, price))

    # Insert transactions
    for prod_name, qty, action in sample_transactions:
        cursor.execute("""
            INSERT INTO transactions (product_name, change_qty, action)
            VALUES (?, ?, ?)
        """, (prod_name, qty, action))

    conn.commit()
    conn.close()
    print("Database successfully seeded with realistic inventory items and logs.")

if __name__ == "__main__":
    seed_database()