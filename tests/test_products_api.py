"""
Unit tests for products API endpoints.

Tests CRUD operations, filtering, and error handling for the products API.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from domain_services.grocery.main import app
from core_services.database.connection import get_session
from core_services.database.models import Product, Store, User


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session.
    
    Returns:
        Session: Test database session
    """
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
    """
    Create a test client with database session override.
    
    Args:
        session: Test database session
        
    Returns:
        TestClient: FastAPI test client
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_store")
def sample_store_fixture(session: Session):
    """
    Create a sample store for testing.
    
    Args:
        session: Database session
        
    Returns:
        Store: Sample store instance
    """
    store = Store(
        name="Test Store",
        location="123 Test St",
        is_active=True
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@pytest.fixture(name="sample_product")
def sample_product_fixture(session: Session, sample_store: Store):
    """
    Create a sample product for testing.
    
    Args:
        session: Database session
        sample_store: Store to associate with product
        
    Returns:
        Product: Sample product instance
    """
    product = Product(
        name="Test Product",
        category="Test Category",
        price=999,  # $9.99
        stock_level=50,
        min_stock_threshold=10,
        store_id=sample_store.id,
        description="A test product"
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


class TestProductsAPI:
    """Test class for products API endpoints."""
    
    def test_get_products_empty(self, client: TestClient):
        """Test getting products when none exist."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_products_with_data(self, client: TestClient, sample_product: Product):
        """Test getting products when data exists."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) == 1
        assert products[0]["name"] == "Test Product"
        assert products[0]["price"] == 999
        assert products[0]["price_dollars"] == 9.99
    
    def test_get_product_by_id_success(self, client: TestClient, sample_product: Product):
        """Test getting a specific product by ID."""
        response = client.get(f"/api/v1/products/{sample_product.id}")
        assert response.status_code == 200
        
        product = response.json()
        assert product["id"] == sample_product.id
        assert product["name"] == "Test Product"
    
    def test_get_product_by_id_not_found(self, client: TestClient):
        """Test getting a non-existent product."""
        response = client.get("/api/v1/products/999")
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]
    
    def test_create_product_success(self, client: TestClient, sample_store: Store):
        """Test creating a new product."""
        product_data = {
            "name": "New Product",
            "category": "New Category",
            "price": 1299,
            "stock_level": 25,
            "min_stock_threshold": 5,
            "store_id": sample_store.id,
            "description": "A new test product"
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 200
        
        product = response.json()
        assert product["name"] == "New Product"
        assert product["price"] == 1299
        assert product["price_dollars"] == 12.99
    
    def test_create_product_invalid_store(self, client: TestClient):
        """Test creating a product with invalid store ID."""
        product_data = {
            "name": "New Product",
            "category": "New Category", 
            "price": 1299,
            "store_id": 999  # Non-existent store
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        assert response.status_code == 400
        assert "Store not found" in response.json()["detail"]
    
    def test_update_product_success(self, client: TestClient, sample_product: Product):
        """Test updating an existing product."""
        update_data = {
            "name": "Updated Product",
            "price": 1599
        }
        
        response = client.put(f"/api/v1/products/{sample_product.id}", json=update_data)
        assert response.status_code == 200
        
        product = response.json()
        assert product["name"] == "Updated Product"
        assert product["price"] == 1599
        assert product["category"] == "Test Category"  # Unchanged
    
    def test_update_product_not_found(self, client: TestClient):
        """Test updating a non-existent product."""
        update_data = {"name": "Updated Product"}
        
        response = client.put("/api/v1/products/999", json=update_data)
        assert response.status_code == 404
    
    def test_delete_product_success(self, client: TestClient, sample_product: Product):
        """Test deleting an existing product."""
        response = client.delete(f"/api/v1/products/{sample_product.id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
    
    def test_delete_product_not_found(self, client: TestClient):
        """Test deleting a non-existent product."""
        response = client.delete("/api/v1/products/999")
        assert response.status_code == 404
    
    def test_filter_products_by_store(self, client: TestClient, sample_product: Product):
        """Test filtering products by store ID."""
        response = client.get(f"/api/v1/products/?store_id={sample_product.store_id}")
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) == 1
        assert products[0]["store_id"] == sample_product.store_id
    
    def test_filter_products_by_category(self, client: TestClient, sample_product: Product):
        """Test filtering products by category."""
        response = client.get("/api/v1/products/?category=Test Category")
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) == 1
        assert products[0]["category"] == "Test Category"
