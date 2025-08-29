"""
Database models for the ModularAI grocery store system.

This module defines the core SQLModel schemas that represent the database tables
and their relationships. All models include proper type hints and validation.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """
    User model for authentication and role management.
    
    Args:
        id: Primary key, auto-generated
        email: User's email address (unique)
        role: User role (manager, data_scientist, customer)
        store_id: Foreign key to associated store (optional for admin users)
        created_at: Timestamp when user was created
        is_active: Whether the user account is active
    
    Returns:
        User: SQLModel instance representing a user
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    role: str = Field(max_length=50)  # manager, data_scientist, customer, admin
    store_id: Optional[int] = Field(default=None, foreign_key="store.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Relationships
    store: Optional["Store"] = Relationship(back_populates="users")
    

class Store(SQLModel, table=True):
    """
    Store model representing physical store locations.
    
    Args:
        id: Primary key, auto-generated
        name: Store name
        location: Store address/location
        created_at: Timestamp when store was created
        is_active: Whether the store is currently active
    
    Returns:
        Store: SQLModel instance representing a store
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    location: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Relationships
    users: List[User] = Relationship(back_populates="store")
    products: List["Product"] = Relationship(back_populates="store")
    transactions: List["Transaction"] = Relationship(back_populates="store")


class Product(SQLModel, table=True):
    """
    Product model with inventory tracking and embeddings for RAG.
    
    Args:
        id: Primary key, auto-generated
        name: Product name
        category: Product category for grouping
        price: Current price in cents (to avoid floating point issues)
        stock_level: Current inventory count
        min_stock_threshold: Minimum stock before alert
        store_id: Foreign key to the store
        description: Product description for embeddings
        embeddings: Vector embeddings for semantic search (JSON array)
        created_at: Timestamp when product was created
        updated_at: Timestamp when product was last updated
    
    Returns:
        Product: SQLModel instance representing a product
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, index=True)
    category: str = Field(max_length=100, index=True)
    price: int = Field(ge=0)  # Price in cents
    stock_level: int = Field(ge=0, default=0)
    min_stock_threshold: int = Field(ge=0, default=10)
    store_id: int = Field(foreign_key="store.id")
    description: Optional[str] = Field(default=None, max_length=1000)
    embeddings: Optional[str] = Field(default=None)  # JSON string of vector embeddings
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    store: Store = Relationship(back_populates="products")
    transactions: List["Transaction"] = Relationship(back_populates="product")
    
    @property
    def price_dollars(self) -> float:
        """Convert price from cents to dollars."""
        return self.price / 100.0
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is below minimum stock threshold."""
        return self.stock_level <= self.min_stock_threshold


class Transaction(SQLModel, table=True):
    """
    Transaction model for recording sales and inventory changes.
    
    Args:
        id: Primary key, auto-generated
        product_id: Foreign key to the product
        store_id: Foreign key to the store
        quantity: Number of items in transaction (negative for returns)
        unit_price: Price per unit at time of transaction (in cents)
        transaction_type: Type of transaction (sale, restock, return, adjustment)
        timestamp: When the transaction occurred
        user_id: Optional foreign key to user who made the transaction
    
    Returns:
        Transaction: SQLModel instance representing a transaction
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    store_id: int = Field(foreign_key="store.id")
    quantity: int = Field()  # Can be negative for returns
    unit_price: int = Field(ge=0)  # Price in cents at time of transaction
    transaction_type: str = Field(max_length=50, default="sale")  # sale, restock, return, adjustment
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Relationships
    product: Product = Relationship(back_populates="transactions")
    store: Store = Relationship(back_populates="transactions")
    
    @property
    def total_amount(self) -> int:
        """Calculate total transaction amount in cents."""
        return self.quantity * self.unit_price
    
    @property
    def total_amount_dollars(self) -> float:
        """Calculate total transaction amount in dollars."""
        return self.total_amount / 100.0


class MLPrediction(SQLModel, table=True):
    """
    Model for storing ML predictions and forecasts.
    
    Args:
        id: Primary key, auto-generated
        product_id: Foreign key to the product
        store_id: Foreign key to the store
        prediction_type: Type of prediction (demand_forecast, stockout_risk)
        predicted_value: The predicted numerical value
        confidence_score: Confidence level of the prediction (0-1)
        prediction_date: Date the prediction was made
        target_date: Date the prediction is for
        model_version: Version of the ML model used
        metadata: Additional prediction metadata as JSON
    
    Returns:
        MLPrediction: SQLModel instance representing an ML prediction
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    store_id: int = Field(foreign_key="store.id")
    prediction_type: str = Field(max_length=100)  # demand_forecast, stockout_risk, etc.
    predicted_value: float = Field()
    confidence_score: float = Field(ge=0.0, le=1.0)
    prediction_date: datetime = Field(default_factory=datetime.utcnow)
    target_date: datetime = Field()
    ml_model_version: str = Field(max_length=50, default="v1.0")
    prediction_metadata: Optional[str] = Field(default=None)  # JSON string for additional data
