"""
Database initialization script.

This module provides functionality to initialize the database with tables
and optionally seed it with sample data for development.
"""

from sqlmodel import Session, select
from core_services.database.connection import engine, create_db_and_tables, get_db_session
from core_services.database.models import User, Store, Product, Transaction
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """
    Initialize the database by creating all tables.
    """
    logger.info("Creating database tables...")
    create_db_and_tables()
    logger.info("Database tables created successfully!")


def seed_sample_data():
    """
    Seed the database with sample data for development and testing.
    
    Creates sample stores, users, products, and transactions.
    """
    session = get_db_session()
    
    try:
        # Check if data already exists
        existing_stores = session.exec(select(Store)).first()
        if existing_stores:
            logger.info("Sample data already exists, skipping seed.")
            return
        
        logger.info("Seeding sample data...")
        
        # Create sample stores
        store1 = Store(
            name="Downtown Grocery",
            location="123 Main St, Downtown",
            is_active=True
        )
        store2 = Store(
            name="Suburban Market",
            location="456 Oak Ave, Suburbs",
            is_active=True
        )
        
        session.add(store1)
        session.add(store2)
        session.commit()
        session.refresh(store1)
        session.refresh(store2)
        
        # Create sample users
        manager1 = User(
            email="manager1@grocery.com",
            role="manager",
            store_id=store1.id,
            is_active=True
        )
        manager2 = User(
            email="manager2@grocery.com", 
            role="manager",
            store_id=store2.id,
            is_active=True
        )
        data_scientist = User(
            email="ds@grocery.com",
            role="data_scientist",
            is_active=True
        )
        
        session.add(manager1)
        session.add(manager2)
        session.add(data_scientist)
        session.commit()
        
        # Create sample products
        products = [
            Product(
                name="Organic Bananas",
                category="Produce",
                price=299,  # $2.99 in cents
                stock_level=50,
                min_stock_threshold=10,
                store_id=store1.id,
                description="Fresh organic bananas, perfect for smoothies and snacks"
            ),
            Product(
                name="Whole Milk",
                category="Dairy",
                price=449,  # $4.49 in cents
                stock_level=25,
                min_stock_threshold=5,
                store_id=store1.id,
                description="Fresh whole milk, locally sourced"
            ),
            Product(
                name="Sourdough Bread",
                category="Bakery",
                price=549,  # $5.49 in cents
                stock_level=15,
                min_stock_threshold=3,
                store_id=store1.id,
                description="Artisan sourdough bread, baked fresh daily"
            ),
            Product(
                name="Ground Coffee",
                category="Beverages",
                price=1299,  # $12.99 in cents
                stock_level=30,
                min_stock_threshold=8,
                store_id=store2.id,
                description="Premium ground coffee beans, medium roast"
            ),
        ]
        
        for product in products:
            session.add(product)
        
        session.commit()
        
        # Create sample transactions
        for product in products:
            session.refresh(product)
            
            # Create a few sample sales transactions
            transaction1 = Transaction(
                product_id=product.id,
                store_id=product.store_id,
                quantity=2,
                unit_price=product.price,
                transaction_type="sale",
                timestamp=datetime.utcnow()
            )
            
            transaction2 = Transaction(
                product_id=product.id,
                store_id=product.store_id,
                quantity=1,
                unit_price=product.price,
                transaction_type="sale",
                timestamp=datetime.utcnow()
            )
            
            session.add(transaction1)
            session.add(transaction2)
        
        session.commit()
        logger.info("Sample data seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding sample data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_database()
    seed_sample_data()
    logger.info("Database initialization completed!")
