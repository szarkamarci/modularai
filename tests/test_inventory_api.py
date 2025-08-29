"""
Unit tests for inventory API endpoints.

Tests stock alerts, inventory status, and stock adjustment functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from domain_services.grocery.main import app
from core_services.database.connection import get_session
from core_services.database.models import Product, Store, Transaction


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="low_stock_product")
def low_stock_product_fixture(session: Session):
    """Create a low stock product for testing."""
    store = Store(name="Test Store", location="Test Location")
    session.add(store)
    session.commit()
    session.refresh(store)
    
    product = Product(
        name="Low Stock Item",
        category="Test",
        price=500,
        stock_level=5,  # Below threshold
        min_stock_threshold=10,
        store_id=store.id
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


class TestInventoryAPI:
    """Test class for inventory API endpoints."""
    
    def test_get_stock_alerts_empty(self, client: TestClient):
        """Test getting stock alerts when none exist."""
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_stock_alerts_with_low_stock(self, client: TestClient, low_stock_product: Product):
        """Test getting stock alerts with low stock items."""
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        
        alerts = response.json()
        assert len(alerts) == 1
        assert alerts[0]["product_id"] == low_stock_product.id
        assert alerts[0]["current_stock"] == 5
        assert alerts[0]["min_threshold"] == 10
    
    def test_get_inventory_status_empty(self, client: TestClient):
        """Test getting inventory status with no products."""
        response = client.get("/api/v1/inventory/status")
        assert response.status_code == 200
        
        status = response.json()
        assert status["total_products"] == 0
        assert status["low_stock_count"] == 0
        assert status["out_of_stock_count"] == 0
        assert status["total_value_cents"] == 0
    
    def test_get_inventory_status_with_products(self, client: TestClient, low_stock_product: Product):
        """Test getting inventory status with products."""
        response = client.get("/api/v1/inventory/status")
        assert response.status_code == 200
        
        status = response.json()
        assert status["total_products"] == 1
        assert status["low_stock_count"] == 1  # Product is low stock
        assert status["out_of_stock_count"] == 0
        assert status["total_value_cents"] == 2500  # 5 * 500
        assert status["total_value_dollars"] == 25.0
    
    def test_adjust_stock_increase(self, client: TestClient, low_stock_product: Product):
        """Test increasing stock levels."""
        adjustment_data = {
            "product_id": low_stock_product.id,
            "adjustment_quantity": 20,
            "reason": "restock"
        }
        
        response = client.post("/api/v1/inventory/adjust", json=adjustment_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["product_id"] == low_stock_product.id
        assert result["previous_stock"] == 5
        assert result["new_stock"] == 25
        assert result["adjustment"] == 20
    
    def test_adjust_stock_decrease(self, client: TestClient, low_stock_product: Product):
        """Test decreasing stock levels."""
        adjustment_data = {
            "product_id": low_stock_product.id,
            "adjustment_quantity": -2,
            "reason": "damage"
        }
        
        response = client.post("/api/v1/inventory/adjust", json=adjustment_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["new_stock"] == 3
        assert result["adjustment"] == -2
    
    def test_adjust_stock_negative_result(self, client: TestClient, low_stock_product: Product):
        """Test adjustment that would result in negative stock."""
        adjustment_data = {
            "product_id": low_stock_product.id,
            "adjustment_quantity": -10,  # Would make stock negative
            "reason": "test"
        }
        
        response = client.post("/api/v1/inventory/adjust", json=adjustment_data)
        assert response.status_code == 400
        assert "negative stock" in response.json()["detail"]
    
    def test_adjust_stock_product_not_found(self, client: TestClient):
        """Test adjusting stock for non-existent product."""
        adjustment_data = {
            "product_id": 999,
            "adjustment_quantity": 10,
            "reason": "test"
        }
        
        response = client.post("/api/v1/inventory/adjust", json=adjustment_data)
        assert response.status_code == 404
    
    def test_get_stock_movements_empty(self, client: TestClient, low_stock_product: Product):
        """Test getting stock movements with no transactions."""
        response = client.get(f"/api/v1/inventory/movements/{low_stock_product.id}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["product_id"] == low_stock_product.id
        assert result["current_stock"] == 5
        assert len(result["movements"]) == 0
    
    def test_get_stock_movements_not_found(self, client: TestClient):
        """Test getting stock movements for non-existent product."""
        response = client.get("/api/v1/inventory/movements/999")
        assert response.status_code == 404
