def setup_category_expense(client, auth_headers):
    """Helper to create an expense category for testing"""
    resp = client.post("/api/categories", json={"name": "Groceries", "type": "expense"}, headers=auth_headers)
    return resp.json()["id"]

def test_create_budget(client, auth_headers):
    """Test creating a budget"""
    category_id = setup_category_expense(client, auth_headers)
    
    response = client.post(
        "/api/budgets/",
        json={
            "name": "Monthly Groceries",
            "category_id": category_id,
            "amount": 300.00,
            "period": "monthly",
            "start_date": "2026-06-01T00:00:00Z",
            "is_active": True
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Monthly Groceries"
    assert response.json()["amount"] == 300.00

def test_get_budgets(client, auth_headers):
    """Test retrieving budgets list"""
    category_id = setup_category_expense(client, auth_headers)
    
    # Create a budget
    client.post("/api/budgets/", json={"name": "Test Budget", "category_id": category_id, "amount": 100.00, "period": "monthly", "start_date": "2026-06-01T00:00:00Z"}, headers=auth_headers)
    
    response = client.get("/api/budgets/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_budget_progress(client, auth_headers):
    """Test retrieving budget progress"""
    category_id = setup_category_expense(client, auth_headers)
    
    # Create budget
    client.post("/api/budgets/", json={"name": "Test Budget", "category_id": category_id, "amount": 100.00, "period": "monthly", "start_date": "2026-06-01T00:00:00Z"}, headers=auth_headers)
    
    response = client.get("/api/budgets/progress", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_budget(client, auth_headers):
    """Test deleting a budget"""
    category_id = setup_category_expense(client, auth_headers)
    
    # Create budget
    create_resp = client.post("/api/budgets/", json={"name": "Test Budget", "category_id": category_id, "amount": 100.00, "period": "monthly", "start_date": "2026-06-01T00:00:00Z"}, headers=auth_headers)
    budget_id = create_resp.json()["id"]
    
    # Delete budget
    response = client.delete(f"/api/budgets/{budget_id}", headers=auth_headers)
    assert response.status_code == 200