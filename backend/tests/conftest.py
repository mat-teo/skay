import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db
from models import User, Account, Transaction, TransactionCategory, Budget
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool  # <--- Importa questo

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, 
    echo=False, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool 
)

def override_get_db():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create all tables before each test."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def client(setup_database):
    """Test client with clean database."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "password": "test123",
        "base_currency": "EUR"
    }

@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token for test user."""
    # Register
    register_response = client.post("/api/auth/register", json=test_user)
    assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
    
    # Login
    login_response = client.post(
        "/api/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    return login_response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}