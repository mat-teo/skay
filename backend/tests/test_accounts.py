def test_create_account(client, auth_headers):
    """Test creating a new account"""
    response = client.post(
        "/api/accounts",
        json={"name": "Cash", "type": "cash", "balance": 1000.00},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Cash"
    assert response.json()["balance"] == 1000.00

def test_get_accounts(client, auth_headers):
    """Test retrieving accounts list"""
    # Create an account first
    client.post("/api/accounts", json={"name": "Cash", "type": "cash", "balance": 500.00}, headers=auth_headers)
    
    response = client.get("/api/accounts", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_update_account(client, auth_headers):
    """Test updating an account"""
    # Create account
    create_resp = client.post("/api/accounts", json={"name": "Cash", "type": "cash", "balance": 500.00}, headers=auth_headers)
    account_id = create_resp.json()["id"]
    
    # Update account
    response = client.put(
        f"/api/accounts/{account_id}",
        json={"name": "Portafoglio", "type": "cash", "balance": 500.00},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Portafoglio"

def test_delete_account(client, auth_headers):
    """Test deleting an account with zero balance"""
    # Create account with zero balance
    create_resp = client.post("/api/accounts", json={"name": "Temp", "type": "cash", "balance": 0.00}, headers=auth_headers)
    account_id = create_resp.json()["id"]
    
    # Delete account
    response = client.delete(f"/api/accounts/{account_id}", headers=auth_headers)
    assert response.status_code == 200