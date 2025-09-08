"""
Database connection and session management for Supabase PostgreSQL.

This module handles the database connection, session creation, and provides
utilities for database operations with proper connection pooling.
"""

import os
import json
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    class Config:
        env_file = ".env"
    """
    Database configuration settings.
    
    Loads configuration from environment variables with validation.
    """
    def __init__(self, **kwargs):

       self.database_url = kwargs.get("database_url", "")
       self.supabase_url = kwargs.get("supabase_url", "")
       self.supabase_anon_key = kwargs.get("supabase_anon_key", "")
       self.supabase_service_key = kwargs.get("supabase_service_key", "")
       self.echo_sql = kwargs.get("echo_sql", False)

def create_db_and_tables(engine):
    """
    Create all database tables based on SQLModel definitions.
    
    This function should be called during application startup to ensure
    all tables exist in the database.
    """
    SQLModel.metadata.create_all(engine)


def get_session(engine) -> Generator[Session, None, None]:
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


def get_db_session(engine) -> Session:
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

def build_engine(setup_path: str):

    with open(setup_path, 'r') as f: #'settings_config_obj.json'
        config_obj = json.load(f)

    # Global settings instance
    settings = DatabaseSettings(config_obj)

    # Create engine with connection pooling
    engine = create_engine(
        settings.database_url,
        echo=settings.echo_sql,
        poolclass=StaticPool,
        connect_args = {
            "check_same_thread": False,  # Only needed for SQLite
        } if "sqlite" in settings.database_url else {},
    )

    return engine



