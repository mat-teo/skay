def test_create_category_expense(client, auth_headers):
    """Test creating an expense category"""
    response = client.post(
        "/api/categories",
        json={"name": "Groceries", "type": "expense"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Groceries"
    assert response.json()["type"] == "expense"

def test_create_category_income(client, auth_headers):
    """Test creating an income category"""
    response = client.post(
        "/api/categories",
        json={"name": "Salary", "type": "income"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Salary"
    assert response.json()["type"] == "income"

def test_get_categories(client, auth_headers):
    """Test retrieving categories list"""
    # Create a category
    client.post("/api/categories", json={"name": "Groceries", "type": "expense"}, headers=auth_headers)
    
    response = client.get("/api/categories", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)