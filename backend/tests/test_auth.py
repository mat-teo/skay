def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    # Register first (only once)
    client.post("/api/auth/register", json=test_user)
    
    # Test wrong password (single attempt)
    response = client.post(
        "/api/auth/login",
        data={"username": test_user["email"], "password": "wrong"}
    )
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    """Test login with non-existent user (single attempt)"""
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent@example.com", "password": "test"}
    )
    assert response.status_code == 401