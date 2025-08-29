"""
Products API routes for inventory and product management.

Provides endpoints for CRUD operations on products, stock level management,
and product search functionality.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel

from core_services.database.connection import get_session
from core_services.database.models import Product, Store

router = APIRouter()


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str
    category: str
    price: int  # Price in cents
    stock_level: int = 0
    min_stock_threshold: int = 10
    store_id: int
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    stock_level: Optional[int] = None
    min_stock_threshold: Optional[int] = None
    description: Optional[str] = None


class ProductResponse(BaseModel):
    """Schema for product response with computed fields."""
    id: int
    name: str
    category: str
    price: int
    price_dollars: float
    stock_level: int
    min_stock_threshold: int
    store_id: int
    description: Optional[str]
    is_low_stock: bool
    created_at: str
    updated_at: str


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip"),
    session: Session = Depends(get_session)
):
    """
    Get all products with optional filtering.
    
    Args:
        store_id: Optional store ID filter
        category: Optional category filter
        low_stock_only: If True, only return products below min stock threshold
        limit: Maximum number of products to return
        offset: Number of products to skip for pagination
        session: Database session
    
    Returns:
        List[ProductResponse]: List of products matching the filters
    """
    query = select(Product)
    
    if store_id:
        query = query.where(Product.store_id == store_id)
    
    if category:
        query = query.where(Product.category == category)
    
    if low_stock_only:
        query = query.where(Product.stock_level <= Product.min_stock_threshold)
    
    query = query.offset(offset).limit(limit)
    products = session.exec(query).all()
    
    return [
        ProductResponse(
            id=product.id,
            name=product.name,
            category=product.category,
            price=product.price,
            price_dollars=product.price_dollars,
            stock_level=product.stock_level,
            min_stock_threshold=product.min_stock_threshold,
            store_id=product.store_id,
            description=product.description,
            is_low_stock=product.is_low_stock,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat()
        )
        for product in products
    ]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    """
    Get a specific product by ID.
    
    Args:
        product_id: Product ID to retrieve
        session: Database session
    
    Returns:
        ProductResponse: Product details
        
    Raises:
        HTTPException: 404 if product not found
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        price=product.price,
        price_dollars=product.price_dollars,
        stock_level=product.stock_level,
        min_stock_threshold=product.min_stock_threshold,
        store_id=product.store_id,
        description=product.description,
        is_low_stock=product.is_low_stock,
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat()
    )


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new product.
    
    Args:
        product_data: Product creation data
        session: Database session
    
    Returns:
        ProductResponse: Created product details
        
    Raises:
        HTTPException: 400 if store doesn't exist
    """
    # Verify store exists
    store = session.get(Store, product_data.store_id)
    if not store:
        raise HTTPException(status_code=400, detail="Store not found")
    
    product = Product(**product_data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        price=product.price,
        price_dollars=product.price_dollars,
        stock_level=product.stock_level,
        min_stock_threshold=product.min_stock_threshold,
        store_id=product.store_id,
        description=product.description,
        is_low_stock=product.is_low_stock,
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat()
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session)
):
    """
    Update an existing product.
    
    Args:
        product_id: Product ID to update
        product_data: Product update data
        session: Database session
    
    Returns:
        ProductResponse: Updated product details
        
    Raises:
        HTTPException: 404 if product not found
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update only provided fields
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    session.commit()
    session.refresh(product)
    
    return ProductResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        price=product.price,
        price_dollars=product.price_dollars,
        stock_level=product.stock_level,
        min_stock_threshold=product.min_stock_threshold,
        store_id=product.store_id,
        description=product.description,
        is_low_stock=product.is_low_stock,
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat()
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a product.
    
    Args:
        product_id: Product ID to delete
        session: Database session
    
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: 404 if product not found
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    session.delete(product)
    session.commit()
    
    return {"message": "Product deleted successfully"}
