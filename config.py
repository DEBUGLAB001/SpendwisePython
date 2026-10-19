import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "spendwise.db")

DEFAULT_MONTHLY_BUDGET = 2000.00

CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Transportation",
    "Housing",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Personal",
    "Other"
]
