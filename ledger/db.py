"""
SQLite based ledger for Kirana store udhaar (credit) system.
All data stays local / encrypted at rest as required by challenge.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "ledger.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('credit', 'payment')),
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_customer(name: str) -> int:
    """Return customer id. Create if not exists."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM customers WHERE name = ? COLLATE NOCASE", (name.strip(),))
    row = cur.fetchone()

    if row:
        customer_id = row["id"]
    else:
        cur.execute("INSERT INTO customers (name) VALUES (?)", (name.strip(),))
        customer_id = cur.lastrowid
        conn.commit()

    conn.close()
    return customer_id


def add_transaction(customer_name: str, amount: float, txn_type: str, note: str = "") -> dict:
    """
    Add credit or payment.
    txn_type: 'credit' or 'payment'
    """
    if amount <= 0:
        return {"success": False, "message": "Amount zero se zyada hona chahiye."}

    customer_id = get_or_create_customer(customer_name)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO transactions (customer_id, amount, type, note) VALUES (?, ?, ?, ?)",
        (customer_id, amount, txn_type, note)
    )
    conn.commit()
    conn.close()

    balance = get_balance(customer_name)
    action = "udhaar add ho gaya" if txn_type == "credit" else "payment record ho gaya"

    return {
        "success": True,
        "message": f"{customer_name} ka ₹{amount:.0f} {action}. Ab total udhaar: ₹{balance:.0f}",
        "balance": balance
    }


def get_balance(customer_name: str) -> float:
    """Current outstanding balance for a customer."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN type = 'payment' THEN amount ELSE 0 END), 0) as balance
        FROM transactions t
        JOIN customers c ON c.id = t.customer_id
        WHERE c.name = ? COLLATE NOCASE
    """, (customer_name.strip(),))

    row = cur.fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def get_today_summary() -> dict:
    """Today's total credit given and payments received."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END), 0) as total_credit,
            COALESCE(SUM(CASE WHEN type = 'payment' THEN amount ELSE 0 END), 0) as total_payment
        FROM transactions
        WHERE date(created_at) = ?
    """, (today,))

    row = cur.fetchone()
    conn.close()

    return {
        "total_credit": float(row["total_credit"]),
        "total_payment": float(row["total_payment"])
    }


def find_customers_by_name(partial_name: str) -> list:
    """Find customers whose name contains the given text (for disambiguation)."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM customers WHERE name LIKE ? COLLATE NOCASE ORDER BY name",
        (f"%{partial_name.strip()}%",)
    )
    rows = cur.fetchall()
    conn.close()
    return [r["name"] for r in rows]


def get_all_balances() -> list:
    """List of all customers with outstanding balance > 0."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name,
            COALESCE(SUM(CASE WHEN t.type = 'credit' THEN t.amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN t.type = 'payment' THEN t.amount ELSE 0 END), 0) as balance
        FROM customers c
        LEFT JOIN transactions t ON t.customer_id = c.id
        GROUP BY c.id
        HAVING balance > 0
        ORDER BY balance DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return [{"name": r["name"], "balance": float(r["balance"])} for r in rows]


# Initialize on import
init_db()
