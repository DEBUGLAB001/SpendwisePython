def test_index_route(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"SpendWise" in res.data
    assert b"Financial Overview" in res.data

def test_create_and_fetch_transaction(client):
    payload = {
        "description": "Monthly Metro Pass",
        "amount": 75.50,
        "category": "Transportation",
        "date": "2026-10-18",
        "notes": "Subway transit card refill"
    }
    create_res = client.post("/api/transactions", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.get_json()["transaction"]
    assert created_data["description"] == "Monthly Metro Pass"
    assert created_data["amount"] == 75.50
    assert created_data["category"] == "Transportation"

    tx_id = created_data["id"]
    fetch_res = client.get(f"/api/transactions/{tx_id}")
    assert fetch_res.status_code == 200
    fetched_data = fetch_res.get_json()
    assert fetched_data["id"] == tx_id
    assert fetched_data["amount"] == 75.50

def test_create_transaction_validation_errors(client):
    # Missing description
    res1 = client.post("/api/transactions", json={"amount": 50, "category": "Food & Dining", "date": "2026-10-10"})
    assert res1.status_code == 400
    assert "Description is required" in res1.get_json()["error"]

    # Negative amount
    res2 = client.post("/api/transactions", json={"description": "Test", "amount": -20, "category": "Other", "date": "2026-10-10"})
    assert res2.status_code == 400
    assert "positive number" in res2.get_json()["error"]

    # Non-numeric amount
    res3 = client.post("/api/transactions", json={"description": "Test", "amount": "invalid", "category": "Other", "date": "2026-10-10"})
    assert res3.status_code == 400
    assert "valid numeric value" in res3.get_json()["error"]

def test_update_transaction(client):
    create_res = client.post("/api/transactions", json={
        "description": "Original Purchase",
        "amount": 40.00,
        "category": "Shopping",
        "date": "2026-10-12"
    })
    tx_id = create_res.get_json()["transaction"]["id"]

    update_res = client.put(f"/api/transactions/{tx_id}", json={
        "description": "Updated Purchase",
        "amount": 65.00,
        "category": "Shopping",
        "date": "2026-10-12",
        "notes": "Added item"
    })
    assert update_res.status_code == 200
    updated = update_res.get_json()["transaction"]
    assert updated["description"] == "Updated Purchase"
    assert updated["amount"] == 65.00
    assert updated["notes"] == "Added item"

def test_delete_transaction(client):
    create_res = client.post("/api/transactions", json={
        "description": "To be removed",
        "amount": 15.00,
        "category": "Other",
        "date": "2026-10-14"
    })
    tx_id = create_res.get_json()["transaction"]["id"]

    del_res = client.delete(f"/api/transactions/{tx_id}")
    assert del_res.status_code == 200
    assert del_res.get_json()["id"] == tx_id

    # Verify not found
    get_res = client.get(f"/api/transactions/{tx_id}")
    assert get_res.status_code == 404

def test_filter_search_and_category(client):
    res = client.get("/api/transactions?category=Transportation")
    assert res.status_code == 200
    items = res.get_json()["items"]
    assert all(t["category"] == "Transportation" for t in items)

    # Search keyword
    search_res = client.get("/api/transactions?search=supermarket")
    assert search_res.status_code == 200
    search_items = search_res.get_json()["items"]
    assert len(search_items) >= 1
    assert "supermarket" in search_items[0]["description"].lower()

def test_pagination(client):
    res = client.get("/api/transactions?page=1&per_page=5")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["items"]) <= 5
    assert data["page"] == 1
    assert data["per_page"] == 5
    assert data["total_count"] > 0
