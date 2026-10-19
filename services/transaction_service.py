import math

def row_to_dict(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "description": row["description"],
        "amount": round(float(row["amount"]), 2),
        "category": row["category"],
        "date": row["date"],
        "notes": row["notes"] or "",
        "created_at": row["created_at"]
    }

def get_all_transactions(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC")
    rows = cursor.fetchall()
    return [row_to_dict(r) for r in rows]

def get_transaction_by_id(db, tx_id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    row = cursor.fetchone()
    return row_to_dict(row)

def create_transaction(db, data):
    cursor = db.cursor()
    description = str(data.get("description", "")).strip()
    amount = float(data.get("amount", 0))
    category = str(data.get("category", "Other")).strip()
    date_val = str(data.get("date", "")).strip()
    notes = str(data.get("notes", "")).strip()

    cursor.execute(
        "INSERT INTO transactions (description, amount, category, date, notes) VALUES (?, ?, ?, ?, ?)",
        (description, amount, category, date_val, notes)
    )
    db.commit()
    new_id = cursor.lastrowid
    return get_transaction_by_id(db, new_id)

def update_transaction(db, tx_id, data):
    existing = get_transaction_by_id(db, tx_id)
    if not existing:
        return None

    description = str(data.get("description", existing["description"])).strip()
    amount = float(data.get("amount", existing["amount"]))
    category = str(data.get("category", existing["category"])).strip()
    date_val = str(data.get("date", existing["date"])).strip()
    notes = str(data.get("notes", existing["notes"])).strip()

    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE transactions
        SET description = ?, amount = ?, category = ?, date = ?, notes = ?
        WHERE id = ?
        """,
        (description, amount, category, date_val, notes, tx_id)
    )
    db.commit()
    return get_transaction_by_id(db, tx_id)

def delete_transaction(db, tx_id):
    existing = get_transaction_by_id(db, tx_id)
    if not existing:
        return False

    cursor = db.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    db.commit()
    return True

def filter_transactions(transactions, search=None, category=None, start_date=None, end_date=None):
    """
    Filter transactions based on search term, category, and date range.
    """
    filtered = []
    search_term = search.lower().strip() if search else None
    cat_filter = category.strip() if category and category != "all" else None

    for t in transactions:
        # Search filter on description or notes
        if search_term:
            desc_match = search_term in t["description"].lower()
            notes_match = search_term in t["notes"].lower()
            if not (desc_match or notes_match):
                continue

        # Category filter
        if cat_filter and t["category"] != cat_filter:
            continue

        # Date range filter
        if start_date and t["date"] < start_date:
            continue
        
        # Range comparison with end_date
        if end_date and t["date"] >= end_date:
            continue

        filtered.append(t)

    return filtered

def sort_transactions(transactions, sort_by="date", direction="desc"):
    """
    Sort transactions by date, amount, or description.
    """
    reverse = (direction.lower() == "desc")
    
    if sort_by == "date":
        key_fn = lambda t: (t["date"], t["id"])
    elif sort_by == "amount":
        key_fn = lambda t: str(t["amount"])
    elif sort_by == "description":
        key_fn = lambda t: t["description"].lower()
    else:
        key_fn = lambda t: (t["date"], t["id"])

    return sorted(transactions, key=key_fn, reverse=reverse)

def paginate_transactions(transactions, page=1, per_page=10):
    """
    Paginate a list of transactions.
    """
    page = max(1, int(page))
    per_page = max(1, min(100, int(per_page)))
    total_count = len(transactions)
    total_pages = max(1, math.ceil(total_count / per_page))

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = transactions[start_idx:end_idx]

    return {
        "items": page_items,
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
