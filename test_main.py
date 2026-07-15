# Test file for Expense Manager API
# Tests all 16 routes with success cases and error handling

import pytest
import uuid
from fastapi.testclient import TestClient
from main import app

# Configure test application
client = TestClient(app)

# ===== FIXTURES =====

@pytest.fixture
def user_token():
    # Create a test user and return the token
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    
    # Register
    response = client.post("/register", json={
        "username": unique_username,
        "password": "senha1234567"
    })
    assert response.status_code == 201
    
    # Login
    response = client.post("/login", json={
        "username": unique_username,
        "password": "senha1234567"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


@pytest.fixture
def categories(user_token):
    # Create test categories and return IDs
    headers = {"Authorization": f"Bearer {user_token}"}
    
    category_ids = []
    categories_data = [
        {"name": "Alimentação", "description": "Comida e bebida"},
        {"name": "Transporte", "description": "Locomoção"},
        {"name": "Entretenimento", "description": "Lazer"}
    ]
    
    for cat in categories_data:
        response = client.post("/categories", json=cat, headers=headers)
        assert response.status_code == 201
        category_ids.append(response.json()["id"])
    
    return category_ids


@pytest.fixture
def expenses(user_token, categories):
    # Create test expenses and return IDs
    headers = {"Authorization": f"Bearer {user_token}"}
    
    expense_ids = []
    expenses_data = [
        {
            "category_id": categories[0],
            "description": "Almoço",
            "amount": "50.50",
            "expense_date": "2026-07-20"
        },
        {
            "category_id": categories[0],
            "description": "Café",
            "amount": "15.00",
            "expense_date": "2026-07-21"
        },
        {
            "category_id": categories[1],
            "description": "Uber",
            "amount": "25.00",
            "expense_date": "2026-07-19"
        }
    ]
    
    for exp in expenses_data:
        response = client.post("/expenses", json=exp, headers=headers)
        assert response.status_code == 201
        expense_ids.append(response.json()["id"])
    
    return expense_ids


# ===== AUTHENTICATION TESTS =====

def test_register_success():
    # Test successful user registration
    unique_username = f"newuser_{uuid.uuid4().hex[:8]}"
    response = client.post("/register", json={
        "username": unique_username,
        "password": "senha1234567"
    })
    assert response.status_code == 201
    assert response.json()["username"] == unique_username
    assert response.json()["message"] == "User created successfully."


def test_register_duplicate_username(user_token):
    # Test registration with duplicate username (should fail)
    response = client.post("/register", json={
        "username": "testuser",
        "password": "outrasenha1234567"
    })
    assert response.status_code == 400
    assert "already in use" in response.json()["detail"]


def test_register_invalid_password():
    # Test registration with password too short (should fail)
    unique_username = f"invalidpass_{uuid.uuid4().hex[:8]}"
    response = client.post("/register", json={
        "username": unique_username,
        "password": "short"
    })
    assert response.status_code == 422  # Validation error


def test_login_success(user_token):
    # Test successful login
    response = client.post("/login", json={
        "username": "testuser",
        "password": "senha1234567"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_username():
    # Test login with non-existent user (should fail)
    response = client.post("/login", json={
        "username": "nonexistentuser12345",
        "password": "senha1234567"
    })
    assert response.status_code == 401
    assert "not found" in response.json()["detail"]


def test_login_wrong_password(user_token):
    # Test login with wrong password (should fail)
    response = client.post("/login", json={
        "username": "testuser",
        "password": "wrongpassword1234567"
    })
    assert response.status_code == 401
    assert "Wrong password" in response.json()["detail"]


# ===== CATEGORIES TESTS =====

def test_create_category_success(user_token):
    # Test successful category creation
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/categories", json={
        "name": "Teste",
        "description": "Categoria de teste"
    }, headers=headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Teste"
    assert "user_id" in response.json()


def test_create_category_no_auth():
    # Test category creation without authentication (should fail)
    response = client.post("/categories", json={
        "name": "Teste",
        "description": "Categoria de teste"
    })
    assert response.status_code == 401


def test_get_categories_success(user_token, categories):
    # Test getting user's categories
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/categories", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 3
    assert response.json()[0]["name"] == "Alimentação"


def test_get_categories_no_auth():
    # Test getting categories without authentication (should fail)
    response = client.get("/categories")
    assert response.status_code == 401


def test_update_category_success(user_token, categories):
    # Test successful category update
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.put(f"/categories/{categories[0]}", json={
        "name": "Alimentação Atualizada",
        "description": "Descrição atualizada"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Alimentação Atualizada"


def test_update_category_not_found(user_token):
    # Test updating non-existent category (should fail)
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.put("/categories/99999", json={
        "name": "Teste",
        "description": "Teste"
    }, headers=headers)
    assert response.status_code == 404


def test_delete_category_success(user_token, categories):
    # Test successful category deletion
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete(f"/categories/{categories[2]}", headers=headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_category_not_found(user_token):
    # Test deleting non-existent category (should fail)
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete("/categories/99999", headers=headers)
    assert response.status_code == 404


# ===== EXPENSES TESTS =====

def test_create_expense_success(user_token, categories):
    # Test successful expense creation
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/expenses", json={
        "category_id": categories[0],
        "description": "Teste expense",
        "amount": "100.00",
        "expense_date": "2026-07-20"
    }, headers=headers)
    assert response.status_code == 201
    assert response.json()["description"] == "Teste expense"
    assert float(response.json()["amount"]) == 100.00


def test_create_expense_invalid_category(user_token):
    # Test creating expense with non-existent category (should fail)
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/expenses", json={
        "category_id": 99999,
        "description": "Teste",
        "amount": "50.00",
        "expense_date": "2026-07-20"
    }, headers=headers)
    assert response.status_code == 404


def test_create_expense_no_auth():
    # Test creating expense without authentication (should fail)
    response = client.post("/expenses", json={
        "category_id": 1,
        "description": "Teste",
        "amount": "50.00",
        "expense_date": "2026-07-20"
    })
    assert response.status_code == 401


def test_get_expenses_success(user_token, expenses):
    # Test getting user's expenses
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/expenses", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 3


def test_get_expenses_no_auth():
    # Test getting expenses without authentication (should fail)
    response = client.get("/expenses")
    assert response.status_code == 401


def test_update_expense_success(user_token, expenses, categories):
    # Test successful expense update
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.put(f"/expenses/{expenses[0]}", json={
        "category_id": categories[1],
        "description": "Expense atualizada",
        "amount": "75.00",
        "expense_date": "2026-07-25"
    }, headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == "Expense atualizada"
    assert float(response.json()["amount"]) == 75.00


def test_update_expense_not_found(user_token, categories):
    # Test updating non-existent expense (should fail)
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.put("/expenses/99999", json={
        "category_id": categories[0],
        "description": "Teste",
        "amount": "50.00",
        "expense_date": "2026-07-20"
    }, headers=headers)
    assert response.status_code == 404


def test_delete_expense_success(user_token, expenses):
    # Test successful expense deletion
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete(f"/expenses/{expenses[2]}", headers=headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_expense_not_found(user_token):
    # Test deleting non-existent expense (should fail)
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.delete("/expenses/99999", headers=headers)
    assert response.status_code == 404


# ===== REPORTS TESTS =====

def test_report_month_success(user_token, expenses):
    # Test monthly report generation
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/report/month/2026-07", headers=headers)
    assert response.status_code == 200
    assert "total_spent" in response.json()
    assert "by_category" in response.json()
    assert response.json()["month"] == "2026-07"


def test_report_month_no_data(user_token):
    # Test monthly report with no data (should return message
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/report/month/2000-01", headers=headers)
    assert response.status_code == 200
    data = response.json()
    if isinstance(data, dict) and "message" in data:
        assert "No data" in data["message"]


def test_report_month_no_auth():
    # Test monthly report without authentication (should fail)
    response = client.get("/report/month/2026-07")
    assert response.status_code == 401


def test_report_category_success(user_token, expenses, categories):
    # Test category report generation
    headers = {"Authorization": f"Bearer {user_token}"}
    # categories[0] has 2 expenses ("Almoço" e "Café")
    response = client.get(f"/report/category/{categories[0]}", headers=headers)
    assert response.status_code == 200
    assert "total_spent" in response.json()
    assert "max_expense" in response.json()
    assert "min_expense" in response.json()
    


def test_report_category_not_found(user_token):
    # Test category report with non-existent category (should fail)
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/report/category/99999", headers=headers)
    assert response.status_code == 404


def test_report_category_no_auth():
    # Test category report without authentication (should fail)
    response = client.get("/report/category/1")
    assert response.status_code == 401


def test_report_comparison_success(user_token):
    # Test month comparison report
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/report/comparison/2026-07", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_report_comparison_no_auth():
    # Test comparison report without authentication (should fail)
    response = client.get("/report/comparison/2026-07")
    assert response.status_code == 401


# ===== SECURITY TESTS =====

def test_access_others_category(user_token, categories):
    # Test that user cannot access another user's category
    # Create another user
    other_username = f"otheruser_{uuid.uuid4().hex[:8]}"
    response = client.post("/register", json={
        "username": other_username,
        "password": "senha1234567"
    })
    
    response = client.post("/login", json={
        "username": other_username,
        "password": "senha1234567"
    })
    other_token = response.json()["access_token"]
    
    # Try to access first user's category
    headers = {"Authorization": f"Bearer {other_token}"}
    response = client.put(f"/categories/{categories[0]}", json={
        "name": "Hacked",
        "description": "Hacked"
    }, headers=headers)
    assert response.status_code == 403


def test_access_others_expense(user_token, expenses):
    # Test that user cannot access another user's expense
    # Create another user
    other_username = f"anotheruser_{uuid.uuid4().hex[:8]}"
    response = client.post("/register", json={
        "username": other_username,
        "password": "senha1234567"
    })
    
    response = client.post("/login", json={
        "username": other_username,
        "password": "senha1234567"
    })
    other_token = response.json()["access_token"]
    
    # Try to access first user's expense (should return 403 Forbidden)
    headers = {"Authorization": f"Bearer {other_token}"}
    response = client.delete(f"/expenses/{expenses[0]}", headers=headers)
    assert response.status_code == 403


# ===== INVALID TOKEN TESTS =====

def test_invalid_token():
    # Test with invalid/expired token
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/categories", headers=headers)
    assert response.status_code == 401


def test_missing_auth_header():
    # Test request without Authorization header
    response = client.get("/categories")
    assert response.status_code == 401