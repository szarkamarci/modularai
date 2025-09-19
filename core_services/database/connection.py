"""
Database connection and session management for Supabase PostgreSQL.

This module handles the database connection, session creation, and provides
utilities for database operations with proper connection pooling.
"""

import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """
    Database configuration settings.
    
    Loads configuration from environment variables with validation.
    """
    database_url: str = "postgresql://postgres:postgres@localhost:54322/postgres"
    supabase_url: str = "http://127.0.0.1:54321"
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    echo_sql: bool = False
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = DatabaseSettings()

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.echo_sql,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,  # Only needed for SQLite
    } if "sqlite" in settings.database_url else {},
)


def create_db_and_tables():
    """
    Create all database tables based on SQLModel definitions.
    
    This function should be called during application startup to ensure
    all tables exist in the database.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLModel database session
        
    Usage:
        @app.get("/products")
        def get_products(session: Session = Depends(get_session)):
            return session.exec(select(Product)).all()
    """
    with Session(engine) as session:
        yield session


def get_db_session() -> Session:
    """
    Get a database session for direct use (not as dependency).
    
    Returns:
        Session: SQLModel database session
        
    Note:
        Remember to close the session when done:
        session = get_db_session()
        try:
            # Your database operations
            pass
        finally:
            session.close()
    """
    return Session(engine)