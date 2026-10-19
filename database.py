import os
import sqlite3
from config import DATABASE_PATH, DATA_DIR, DEFAULT_MONTHLY_BUDGET

def get_db(db_path=None):
    path = db_path or DATABASE_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    path = db_path or DATABASE_PATH
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = get_db(path)
    cursor = conn.cursor()

    # Create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create settings table for budget and preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Seed default budget if missing
    cursor.execute("SELECT value FROM settings WHERE key = 'monthly_budget'")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO settings (key, value) VALUES ('monthly_budget', ?)", (str(DEFAULT_MONTHLY_BUDGET),))

    # Seed transactions if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM transactions")
    count_row = cursor.fetchone()
    if count_row and count_row["count"] == 0:
        seed_data = [
            ("Housing Rent", 950.00, "Housing", "2026-10-01", "Monthly apartment lease"),
            ("Supermarket Fresh Produce", 84.50, "Groceries", "2026-10-02", "Organic vegetables and fruits"),
            ("Electric & Water Utility", 115.00, "Utilities", "2026-10-03", "City power utility"),
            ("Downtown Bistro Dinner", 45.00, "Food & Dining", "2026-10-05", "Dinner with colleagues"),
            ("Monthly Transit Pass", 60.00, "Transportation", "2026-10-07", "Metro and bus pass"),
            ("Pharmacy Prescription", 28.00, "Healthcare", "2026-10-08", "Vitamins and allergy medicine"),
            ("Coffee & Bakery", 14.50, "Food & Dining", "2026-10-10", "Morning coffee meetings"),
            ("Streaming Entertainment", 24.99, "Entertainment", "2026-10-12", "Video and music subscriptions"),
            ("Artisan Grocery Store", 36.00, "Groceries", "2026-10-14", "Dairy and bakery goods"),
            ("Gasoline Refill", 55.00, "Transportation", "2026-10-15", "Highway gas station"),
            ("Home Hardware Tools", 95.00, "Shopping", "2026-10-16", "Drill bits and shelf brackets"),
            ("Cinema Tickets", 32.00, "Entertainment", "2026-10-17", "Weekend movie screening"),
            ("Fast Casual Lunch", 22.50, "Food & Dining", "2026-10-18", "Sandwich and salad combo"),
            ("High Speed Fiber Internet", 70.00, "Utilities", "2026-10-19", "Broadband monthly charge"),
            ("Previous Month Market", 120.00, "Groceries", "2026-09-15", "Bulk groceries September"),
            ("Auto Service & Oil", 180.00, "Transportation", "2026-09-28", "Routine maintenance September")
        ]
        cursor.executemany(
            "INSERT INTO transactions (description, amount, category, date, notes) VALUES (?, ?, ?, ?, ?)",
            seed_data
        )

    conn.commit()
    conn.close()
