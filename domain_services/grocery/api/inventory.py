"""
Inventory API routes for stock management and alerts.

Provides endpoints for inventory tracking, stock alerts, and inventory
adjustment operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime

from core_services.database.connection import get_session
from core_services.database.models import Product, Transaction

router = APIRouter()


class StockAlert(BaseModel):
    """Schema for stock alert information."""
    product_id: int
    product_name: str
    category: str
    current_stock: int
    min_threshold: int
    store_id: int
    store_name: Optional[str] = None
    days_until_stockout: Optional[int] = None


class StockAdjustment(BaseModel):
    """Schema for stock level adjustments."""
    product_id: int
    adjustment_quantity: int  # Positive for restock, negative for removal
    reason: str = "manual_adjustment"


class InventoryResponse(BaseModel):
    """Schema for inventory status response."""
    total_products: int
    low_stock_count: int
    out_of_stock_count: int
    total_value_cents: int
    total_value_dollars: float


@router.get("/alerts", response_model=List[StockAlert])
async def get_stock_alerts(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    session: Session = Depends(get_session)
):
    """
    Get current stockout warnings and low stock alerts.
    
    Args:
        store_id: Optional store ID filter
        session: Database session
    
    Returns:
        List[StockAlert]: List of products requiring attention
    """
    query = select(Product).where(Product.stock_level <= Product.min_stock_threshold)
    
    if store_id:
        query = query.where(Product.store_id == store_id)
    
    low_stock_products = session.exec(query).all()
    
    alerts = []
    for product in low_stock_products:
        # Reason: Calculate estimated days until stockout based on recent sales
        # This is a simplified calculation - in production, would use ML predictions
        recent_transactions = session.exec(
            select(Transaction)
            .where(Transaction.product_id == product.id)
            .where(Transaction.transaction_type == "sale")
            .order_by(Transaction.timestamp.desc())
            .limit(30)
        ).all()
        
        days_until_stockout = None
        if recent_transactions:
            total_sold = sum(abs(t.quantity) for t in recent_transactions)
            avg_daily_sales = total_sold / min(30, len(recent_transactions))
            if avg_daily_sales > 0:
                days_until_stockout = max(0, int(product.stock_level / avg_daily_sales))
        
        alerts.append(StockAlert(
            product_id=product.id,
            product_name=product.name,
            category=product.category,
            current_stock=product.stock_level,
            min_threshold=product.min_stock_threshold,
            store_id=product.store_id,
            days_until_stockout=days_until_stockout
        ))
    
    return alerts


@router.get("/status", response_model=InventoryResponse)
async def get_inventory_status(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    session: Session = Depends(get_session)
):
    """
    Get overall inventory status and metrics.
    
    Args:
        store_id: Optional store ID filter
        session: Database session
    
    Returns:
        InventoryResponse: Inventory summary statistics
    """
    query = select(Product)
    if store_id:
        query = query.where(Product.store_id == store_id)
    
    products = session.exec(query).all()
    
    total_products = len(products)
    low_stock_count = sum(1 for p in products if p.is_low_stock)
    out_of_stock_count = sum(1 for p in products if p.stock_level == 0)
    total_value_cents = sum(p.stock_level * p.price for p in products)
    
    return InventoryResponse(
        total_products=total_products,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        total_value_cents=total_value_cents,
        total_value_dollars=total_value_cents / 100.0
    )


@router.post("/adjust")
async def adjust_stock(
    adjustment: StockAdjustment,
    session: Session = Depends(get_session)
):
    """
    Adjust stock levels for a product and record the transaction.
    
    Args:
        adjustment: Stock adjustment details
        session: Database session
    
    Returns:
        dict: Success message with new stock level
        
    Raises:
        HTTPException: 404 if product not found, 400 for invalid adjustment
    """
    product = session.get(Product, adjustment.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if adjustment would result in negative stock
    new_stock_level = product.stock_level + adjustment.adjustment_quantity
    if new_stock_level < 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Adjustment would result in negative stock. Current: {product.stock_level}, Adjustment: {adjustment.adjustment_quantity}"
        )
    
    # Update stock level
    product.stock_level = new_stock_level
    product.updated_at = datetime.utcnow()
    
    # Record the adjustment as a transaction
    transaction = Transaction(
        product_id=product.id,
        store_id=product.store_id,
        quantity=adjustment.adjustment_quantity,
        unit_price=product.price,
        transaction_type="adjustment" if adjustment.adjustment_quantity != 0 else "restock",
        timestamp=datetime.utcnow()
    )
    
    session.add(transaction)
    session.commit()
    session.refresh(product)
    
    return {
        "message": "Stock adjusted successfully",
        "product_id": product.id,
        "previous_stock": product.stock_level - adjustment.adjustment_quantity,
        "new_stock": product.stock_level,
        "adjustment": adjustment.adjustment_quantity
    }


@router.get("/movements/{product_id}")
async def get_stock_movements(
    product_id: int,
    limit: int = Query(50, ge=1, le=500, description="Maximum number of movements to return"),
    session: Session = Depends(get_session)
):
    """
    Get recent stock movements for a specific product.
    
    Args:
        product_id: Product ID to get movements for
        limit: Maximum number of movements to return
        session: Database session
    
    Returns:
        List[dict]: List of recent stock movements
        
    Raises:
        HTTPException: 404 if product not found
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    transactions = session.exec(
        select(Transaction)
        .where(Transaction.product_id == product_id)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
    ).all()
    
    movements = []
    for transaction in transactions:
        movements.append({
            "id": transaction.id,
            "quantity": transaction.quantity,
            "transaction_type": transaction.transaction_type,
            "unit_price": transaction.unit_price,
            "unit_price_dollars": transaction.unit_price / 100.0,
            "total_amount": transaction.total_amount,
            "total_amount_dollars": transaction.total_amount_dollars,
            "timestamp": transaction.timestamp.isoformat()
        })
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "current_stock": product.stock_level,
        "movements": movements
    }
