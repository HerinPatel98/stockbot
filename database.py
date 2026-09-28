import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

DB_NAME = "inventory.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

def hash_password(password: str) -> str:
    """Produces SHA-256 hash for secure credential storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initializes schema with authentication, wallets, telemetry, and tenant scoping."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Clients Table (Tenants & Dummy USD Wallets)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL UNIQUE,
            contact_email TEXT,
            rate_per_query REAL DEFAULT 0.05,
            wallet_balance REAL DEFAULT 25.00,
            low_balance_threshold REAL DEFAULT 2.00,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'suspended', 'depleted')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Users Table (Authentication & RBAC)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'client_admin', 'client_staff')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)

    # 3. Client-Scoped Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            stock INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            UNIQUE(client_id, name)
        )
    """)

    # 4. Client-Scoped Transactions Table (Activity Ledger)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity_change INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)

    # 5. Zero-Knowledge Telemetry Ledger (Admin Billing - No Prompt or Product Leakage)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_billing_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            model_used TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            total_tokens INTEGER NOT NULL,
            cost_deducted REAL NOT NULL,
            balance_after REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # 6. Wallet Deposit Ledger (Recharge History)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallet_topups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            amount_added REAL NOT NULL,
            payment_reference TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    """)

    conn.commit()

    # Seed initial test data if table is empty
    cursor.execute("SELECT COUNT(*) FROM clients")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO clients (company_name, contact_email, rate_per_query, wallet_balance) VALUES ('Acme Corp', 'ops@acme.com', 0.05, 25.00)")
        cursor.execute("INSERT INTO clients (company_name, contact_email, rate_per_query, wallet_balance) VALUES ('Stark Logistics', 'tony@stark.com', 0.08, 50.00)")
        conn.commit()

        cursor.execute("INSERT INTO users (client_id, username, password_hash, role) VALUES (NULL, 'admin', ?, 'admin')", (hash_password("admin123"),))
        cursor.execute("INSERT INTO users (client_id, username, password_hash, role) VALUES (1, 'acme_admin', ?, 'client_admin')", (hash_password("pass123"),))
        cursor.execute("INSERT INTO users (client_id, username, password_hash, role) VALUES (2, 'stark_admin', ?, 'client_admin')", (hash_password("pass123"),))
        conn.commit()

        # Seed products for Acme Corp (client_id = 1)
        cursor.execute("INSERT INTO products (client_id, name, stock, price) VALUES (1, 'Ergonomic Desk', 15, 120.00)")
        cursor.execute("INSERT INTO products (client_id, name, stock, price) VALUES (1, 'Mechanical Keyboard', 45, 65.00)")
        cursor.execute("INSERT INTO products (client_id, name, stock, price) VALUES (1, 'USB-C Dock', 30, 49.99)")
        
        # Seed products for Stark Logistics (client_id = 2)
        cursor.execute("INSERT INTO products (client_id, name, stock, price) VALUES (2, 'Arc Reactor Core', 5, 9999.00)")
        cursor.execute("INSERT INTO products (client_id, name, stock, price) VALUES (2, 'Titanium Alloy Plate', 200, 150.00)")
        conn.commit()

    conn.close()

def verify_user(username: str, password_raw: str):
    """Validates login credentials against stored hashes."""
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password_raw)
    
    cursor.execute("""
        SELECT u.id, u.client_id, u.username, u.role, c.company_name, c.wallet_balance, c.rate_per_query
        FROM users u
        LEFT JOIN clients c ON u.client_id = c.id
        WHERE u.username = ? AND u.password_hash = ?
    """, (username, pwd_hash))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None
    
    return {
        "user_id": user[0],
        "client_id": user[1],
        "username": user[2],
        "role": user[3],
        "company_name": user[4] or "Platform Administrator",
        "wallet_balance": user[5] or 0.0,
        "rate_per_query": user[6] or 0.0
    }

def record_zero_knowledge_billing(client_id: int, user_id: int, model: str, p_tokens: int, c_tokens: int):
    """Deducts per-query rate from tenant wallet and logs numeric telemetry."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT wallet_balance, rate_per_query FROM clients WHERE id = ?", (client_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return 0.0, 0.0

    current_bal, rate = row
    if current_bal < rate:
        conn.close()
        raise ValueError("Insufficient wallet balance.")

    new_balance = round(current_bal - rate, 4)
    total_tokens = p_tokens + c_tokens

    cursor.execute("UPDATE clients SET wallet_balance = ? WHERE id = ?", (new_balance, client_id))
    cursor.execute("""
        INSERT INTO api_billing_telemetry 
        (client_id, user_id, model_used, prompt_tokens, completion_tokens, total_tokens, cost_deducted, balance_after)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (client_id, user_id, model, p_tokens, c_tokens, total_tokens, rate, new_balance))

    conn.commit()
    conn.close()
    return rate, new_balance

def top_up_client_wallet(client_id: int, amount: float, reference: str):
    """Adds dummy dollars to client wallet and records recharge log."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clients SET wallet_balance = wallet_balance + ? WHERE id = ?", (amount, client_id))
    cursor.execute("""
        INSERT INTO wallet_topups (client_id, amount_added, payment_reference)
        VALUES (?, ?, ?)
    """, (client_id, amount, reference))
    conn.commit()
    cursor.execute("SELECT wallet_balance FROM clients WHERE id = ?", (client_id,))
    new_bal = cursor.fetchone()[0]
    conn.close()
    return new_bal

def fetch_client_products(client_id: int):
    conn = get_connection()
    df = pd.read_sql("SELECT name AS Product, stock AS Stock, price AS Price FROM products WHERE client_id = ?", conn, params=(client_id,))
    conn.close()
    return df

def fetch_client_transactions(client_id: int, limit: int = 50):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT product_name AS Product, quantity_change AS Change, action_type AS Type, timestamp AS Time
        FROM transactions 
        WHERE client_id = ?
        ORDER BY id DESC LIMIT ?
    """, conn, params=(client_id, limit))
    conn.close()
    return df

def fetch_client_telemetry(client_id: int):
    conn = get_connection()
    df = pd.read_sql("""
        SELECT id AS 'Log ID', model_used AS Engine, total_tokens AS 'Total Tokens', 
               cost_deducted AS 'Cost ($)', balance_after AS 'Balance After ($)', timestamp AS Timestamp
        FROM api_billing_telemetry
        WHERE client_id = ?
        ORDER BY id DESC
    """, conn, params=(client_id,))
    conn.close()
    return df
    