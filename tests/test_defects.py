from services.transaction_service import filter_transactions, sort_transactions
from services.analytics_service import get_category_breakdown

def test_range_aggregation_inclusive_boundary():
    """
    Bug 1 (DSA: Range Aggregation):
    Date range filtering and period aggregation must include transactions
    occurring on the end date boundary (inclusive end date).
    """
    sample_transactions = [
        {"id": 1, "description": "Start of month purchase", "amount": 50.0, "category": "Shopping", "date": "2026-10-01", "notes": ""},
        {"id": 2, "description": "Mid-month purchase", "amount": 35.0, "category": "Groceries", "date": "2026-10-10", "notes": ""},
        {"id": 3, "description": "End-boundary purchase", "amount": 45.0, "category": "Utilities", "date": "2026-10-15", "notes": ""},
        {"id": 4, "description": "Post-boundary purchase", "amount": 80.0, "category": "Housing", "date": "2026-10-20", "notes": ""}
    ]

    # Query range from 2026-10-01 to 2026-10-15
    results = filter_transactions(sample_transactions, start_date="2026-10-01", end_date="2026-10-15")
    result_ids = [t["id"] for t in results]

    assert 3 in result_ids, (
        f"Expected transaction on end date 2026-10-15 (id=3) to be included in range results, "
        f"but got ids: {result_ids}"
    )
    total_spent = sum(t["amount"] for t in results)
    assert total_spent == 130.0, f"Expected total $130.00 within range, got ${total_spent:.2f}"

def test_amount_sorting_numeric_order():
    """
    Bug 2 (DSA: Sorting or Selection):
    Sorting transactions by amount must sort numerically by monetary value,
    not lexicographically as strings.
    """
    sample_transactions = [
        {"id": 1, "description": "Small snack", "amount": 95.0, "category": "Food & Dining", "date": "2026-10-01"},
        {"id": 2, "description": "Major appliance", "amount": 850.0, "category": "Shopping", "date": "2026-10-02"},
        {"id": 3, "description": "Monthly rent", "amount": 1000.0, "category": "Housing", "date": "2026-10-03"}
    ]

    # Sort by amount descending
    sorted_txs = sort_transactions(sample_transactions, sort_by="amount", direction="desc")
    sorted_amounts = [t["amount"] for t in sorted_txs]

    assert sorted_amounts == [1000.0, 850.0, 95.0], (
        f"Expected descending numerical order [1000.0, 850.0, 95.0], but got {sorted_amounts}"
    )

def test_category_breakdown_accumulation():
    """
    Bug 3 (DSA: Grouping or Filtering):
    Category breakdown must aggregate all spending across disjoint,
    non-consecutive transactions belonging to the same category.
    """
    sample_transactions = [
        {"id": 1, "description": "Lunch meeting", "amount": 30.0, "category": "Food & Dining"},
        {"id": 2, "description": "Train ticket", "amount": 50.0, "category": "Transportation"},
        {"id": 3, "description": "Dinner takeout", "amount": 40.0, "category": "Food & Dining"}
    ]

    breakdown = get_category_breakdown(sample_transactions)
    food_total = breakdown.get("Food & Dining", 0.0)

    assert food_total == 70.0, (
        f"Expected category 'Food & Dining' total to accumulate to $70.00, but got ${food_total:.2f}"
    )

def test_budget_update_payload_integration(client):
    """
    Bug 4 (Error Handling / Integration):
    The budget update endpoint must accept the payload format sent by the frontend UI
    ({'amount': ...}) and persist the updated monthly budget.
    """
    # The frontend submits: { "amount": 2500.0 }
    res = client.post("/api/budget", json={"amount": 2500.0})
    
    assert res.status_code == 200, (
        f"Expected HTTP 200 when updating budget via UI payload, got {res.status_code}: {res.get_data(as_text=True)}"
    )
    data = res.get_json()
    assert data["budget"]["budget_limit"] == 2500.0, (
        f"Expected budget limit to be 2500.0, got {data.get('budget', {}).get('budget_limit')}"
    )
