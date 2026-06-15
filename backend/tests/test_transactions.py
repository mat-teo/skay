def setup_accounts(client, auth_headers):
    """Helper to create accounts for testing"""
    client.post("/api/accounts", json={"name": "Cash", "type": "cash", "balance": 1000.00}, headers=auth_headers)
    client.post("/api/accounts", json={"name": "Bank", "type": "bank", "balance": 2000.00}, headers=auth_headers)

def setup_category(client, auth_headers):
    """Helper to create a category for testing"""
    resp = client.post("/api/categories", json={"name": "Groceries", "type": "expense"}, headers=auth_headers)
    return resp.json()["id"]

def test_create_transaction_expense(client, auth_headers):
    """Test creating an expense transaction"""
    setup_accounts(client, auth_headers)
    category_id = setup_category(client, auth_headers)
    
    response = client.post(
        "/api/transactions",
        json={
            "amount": 50.00,
            "type": "expense",
            "category_id": category_id,
            "account_source_id": 1,
            "notes": "Supermarket"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 50.00
    assert response.json()["type"] == "expense"

def test_create_transaction_income(client, auth_headers):
    """Test creating an income transaction"""
    setup_accounts(client, auth_headers)
    
    response = client.post(
        "/api/transactions",
        json={
            "amount": 2000.00,
            "type": "income",
            "account_destination_id": 2,
            "notes": "Salary"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 2000.00
    assert response.json()["type"] == "income"

def test_get_transactions(client, auth_headers):
    """Test retrieving transactions list"""
    setup_accounts(client, auth_headers)
    
    response = client.get("/api/transactions", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_transaction(client, auth_headers):
    """Test deleting a transaction"""
    setup_accounts(client, auth_headers)
    category_id = setup_category(client, auth_headers)
    
    # Create transaction
    create_resp = client.post(
        "/api/transactions",
        json={"amount": 50.00, "type": "expense", "category_id": category_id, "account_source_id": 1},
        headers=auth_headers
    )
    tx_id = create_resp.json()["id"]
    
    # Delete transaction
    response = client.delete(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert response.status_code == 200