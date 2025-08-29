"""
Main FastAPI application for the grocery domain service.

This is the entry point for the grocery store API, providing endpoints for
inventory management, demand forecasting, and RAG chatbot functionality.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core_services.database.connection import create_db_and_tables
from domain_services.grocery.api.products import router as products_router
from domain_services.grocery.api.inventory import router as inventory_router
from domain_services.grocery.api.chat import router as chat_router
from domain_services.grocery.api.ml import router as ml_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting ModularAI Grocery Service...")
    create_db_and_tables()
    logger.info("Database tables initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ModularAI Grocery Service...")


# Create FastAPI application
app = FastAPI(
    title="ModularAI - Grocery Store API",
    description="AI-powered grocery store management system with predictive analytics and RAG chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Vue.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(ml_router, prefix="/api/v1/ml", tags=["machine-learning"])


@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API information and available endpoints
    """
    return {
        "message": "ModularAI Grocery Store API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "products": "/api/v1/products",
            "inventory": "/api/v1/inventory", 
            "chat": "/api/v1/chat",
            "ml": "/api/v1/ml"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "grocery-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "domain_services.grocery.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
