from services.budget_service import calculate_budget_status

def test_budget_status_normal():
    status = calculate_budget_status(total_spent=500.0, budget_limit=1000.0)
    assert status["status"] == "normal"
    assert status["remaining"] == 500.0
    assert status["utilization_percentage"] == 50.0

def test_budget_status_warning():
    status = calculate_budget_status(total_spent=850.0, budget_limit=1000.0)
    assert status["status"] == "warning"
    assert status["remaining"] == 150.0
    assert status["utilization_percentage"] == 85.0

def test_budget_status_exceeded():
    status = calculate_budget_status(total_spent=1100.0, budget_limit=1000.0)
    assert status["status"] == "exceeded"
    assert status["remaining"] == -100.0
    assert status["utilization_percentage"] == 110.0

def test_get_budget_api(client):
    res = client.get("/api/budget")
    assert res.status_code == 200
    data = res.get_json()
    assert "budget_limit" in data
    assert "total_spent" in data
    assert "remaining" in data
    assert "status" in data
