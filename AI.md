# SpendWise

## Description
SpendWise is a lightweight, full-stack financial expense and budget tracking application designed to help users record transactions, monitor monthly budgets, and analyze spending patterns. The backend is built with Python and Flask, exposing RESTful endpoints for transaction CRUD operations, budget tracking, and spending analytics. The application entry point is `app.py`, which initializes the SQLite database and registers API blueprints from `routes/api.py` and UI routing from `routes/web.py`. Core business logic and data processing algorithms reside in `services/transaction_service.py`, `services/budget_service.py`, and `services/analytics_service.py`. Relational data persistence is managed through SQLite in `database.py` with the database file located at `data/spendwise.db`. The frontend is a single-page interface powered by vanilla JavaScript (`static/js/app.js`), semantic HTML (`templates/index.html`), and custom CSS (`static/css/style.css`).

## Repository Structure
```
.
├── app.py                      # Flask application factory and entry point
├── challenge.json              # Platform runtime and challenge specification
├── config.py                   # Configuration constants, paths, and categories
├── database.py                 # SQLite schema initialization and seed data
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── data/
│   └── spendwise.db            # Local SQLite database
├── routes/
│   ├── __init__.py
│   ├── api.py                  # REST API routes for transactions, budgets, analytics
│   └── web.py                  # Web route serving frontend dashboard
├── services/
│   ├── __init__.py
│   ├── analytics_service.py    # Spending summaries, breakdown, and monthly trends
│   ├── budget_service.py       # Budget limits, status, and threshold checks
│   └── transaction_service.py  # Transaction CRUD, filtering, sorting, pagination
├── static/
│   ├── css/
│   │   └── style.css           # Financial SaaS UI stylesheet
│   └── js/
│       └── app.js              # Client-side reactivity, API client, and modals
└── templates/
    └── index.html              # Single-page dashboard template
```

## Bugs and Bug Locations

1. Range Aggregation Inclusive Boundary Defect
- Bug location: `services/transaction_service.py`, within `filter_transactions()` (line 102).
- How to observe it: Filter transactions or request summary analytics with `start_date="2026-10-01"` and `end_date="2026-10-15"`.
- Failure: Transactions occurring on the boundary date `2026-10-15` (e.g., "Gasoline Refill") are excluded from the returned list and total calculations because the date filter uses strict inequality `t["date"] >= end_date` instead of `> end_date`.
- Expected: Date range filtering must be boundary-inclusive (`t["date"] <= end_date`), ensuring transactions occurring on the end date are included in both filtered records and range totals.

2. Transaction Amount String Sorting Defect
- Bug location: `services/transaction_service.py`, within `sort_transactions()` (line 117).
- How to observe it: Sort transactions by amount descending in the Transactions table or call `sort_transactions()` with `sort_by="amount"` and `direction="desc"`.
- Failure: Transactions sort in alphabetical lexicographical string order because the sort key converts float amounts to strings (`key_fn = lambda t: str(t["amount"])`), placing `$95.00` before `$850.00` and `$1000.00`.
- Expected: Transactions must sort according to numeric value (`key_fn = lambda t: float(t["amount"])`), ordering amounts in correct numerical sequence (`$1000.00` > `$850.00` > `$95.00`).

3. Category Spending Breakdown Accumulation Defect
- Bug location: `services/analytics_service.py`, within `get_category_breakdown()` (lines 11–14).
- How to observe it: Inspect the "Spending by Category" panel on the Overview or Analytics tab for categories with non-contiguous records (e.g., "Food & Dining").
- Failure: `itertools.groupby` only groups consecutive items with identical keys; when iterating over unsorted transactions, disjoint groups of the same category overwrite previous totals in `breakdown[category]` instead of accumulating them, undercounting category sums and reporting inaccurate top categories.
- Expected: Category breakdown aggregation must accumulate total spending for every transaction matching each category across the entire dataset.

4. Budget Update Payload Key Mismatch
- Bug location: `routes/api.py`, within `update_budget_route()` (line 186).
- How to observe it: Enter a new budget amount in the "Adjust Monthly Budget" form on the Budgets tab and click "Save Budget", or send a `POST /api/budget` request with payload `{"amount": 2500.0}`.
- Failure: The backend route strictly validates the presence of `"monthly_budget"` in `request.get_json()` and rejects requests containing `"amount"` with HTTP 400 Bad Request (`{"error": "Missing required field: 'monthly_budget'"}`), causing the UI update to fail.
- Expected: The endpoint must accept the payload key sent by the client (`amount` or `monthly_budget`), update the monthly budget ceiling in SQLite, and return HTTP 200 with the updated budget status.
