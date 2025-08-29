"""
Machine Learning API routes for demand forecasting and predictions.

Provides endpoints for ML model training, predictions, and analytics.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel
from datetime import datetime, timedelta

from core_services.database.connection import get_session
from core_services.database.models import Product, Transaction, MLPrediction

router = APIRouter()


class ForecastRequest(BaseModel):
    """Schema for demand forecast request."""
    product_id: int
    days_ahead: int = 7
    confidence_level: float = 0.95


class ForecastResponse(BaseModel):
    """Schema for demand forecast response."""
    product_id: int
    product_name: str
    forecast_days: int
    predicted_demand: float
    confidence_score: float
    recommendation: str
    historical_avg: float


class ModelTrainingRequest(BaseModel):
    """Schema for model training request."""
    model_type: str = "demand_forecast"
    store_id: Optional[int] = None
    retrain_all: bool = False


@router.post("/{product_id}/forecast", response_model=ForecastResponse)
async def get_demand_predictions(
    product_id: int,
    forecast_request: ForecastRequest,
    session: Session = Depends(get_session)
):
    """
    Get demand predictions for a specific product.
    
    Args:
        product_id: Product ID to forecast
        forecast_request: Forecast parameters
        session: Database session
    
    Returns:
        ForecastResponse: Demand forecast with recommendations
        
    Raises:
        HTTPException: 404 if product not found
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get historical transaction data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Look at last 30 days
    
    transactions = session.exec(
        select(Transaction)
        .where(Transaction.product_id == product_id)
        .where(Transaction.transaction_type == "sale")
        .where(Transaction.timestamp >= start_date)
        .where(Transaction.timestamp <= end_date)
    ).all()
    
    if not transactions:
        # No historical data - return conservative estimate
        return ForecastResponse(
            product_id=product_id,
            product_name=product.name,
            forecast_days=forecast_request.days_ahead,
            predicted_demand=0.0,
            confidence_score=0.1,
            recommendation="Insufficient historical data for accurate forecasting",
            historical_avg=0.0
        )
    
    # Simple forecasting algorithm (would be replaced with actual ML model)
    # Reason: Calculate average daily demand from historical data
    total_sold = sum(abs(t.quantity) for t in transactions)
    days_of_data = (end_date - start_date).days
    daily_avg = total_sold / max(1, days_of_data)
    
    # Project forward
    predicted_demand = daily_avg * forecast_request.days_ahead
    
    # Simple confidence calculation based on data consistency
    daily_sales = {}
    for transaction in transactions:
        date_key = transaction.timestamp.date()
        daily_sales[date_key] = daily_sales.get(date_key, 0) + abs(transaction.quantity)
    
    if len(daily_sales) > 1:
        sales_values = list(daily_sales.values())
        avg_sales = sum(sales_values) / len(sales_values)
        variance = sum((x - avg_sales) ** 2 for x in sales_values) / len(sales_values)
        confidence = max(0.1, min(0.9, 1.0 - (variance / max(1, avg_sales))))
    else:
        confidence = 0.3
    
    # Generate recommendation
    current_stock = product.stock_level
    if predicted_demand > current_stock:
        recommendation = f"Recommend restocking: predicted demand ({predicted_demand:.1f}) exceeds current stock ({current_stock})"
    elif predicted_demand < current_stock * 0.3:
        recommendation = f"Stock levels adequate: predicted demand ({predicted_demand:.1f}) is well below current stock"
    else:
        recommendation = f"Monitor closely: predicted demand ({predicted_demand:.1f}) is moderate relative to stock ({current_stock})"
    
    return ForecastResponse(
        product_id=product_id,
        product_name=product.name,
        forecast_days=forecast_request.days_ahead,
        predicted_demand=predicted_demand,
        confidence_score=confidence,
        recommendation=recommendation,
        historical_avg=daily_avg
    )


@router.post("/retrain")
async def retrain_models(
    training_request: ModelTrainingRequest,
    session: Session = Depends(get_session)
):
    """
    Trigger model retraining with latest data.
    
    Args:
        training_request: Training parameters
        session: Database session
    
    Returns:
        dict: Training status and results
    """
    # Placeholder for actual model training
    # In production, this would:
    # 1. Fetch latest transaction data
    # 2. Prepare training datasets
    # 3. Train/update ML models
    # 4. Validate model performance
    # 5. Deploy updated models
    
    query = select(Product)
    if training_request.store_id:
        query = query.where(Product.store_id == training_request.store_id)
    
    products = session.exec(query).all()
    
    return {
        "status": "completed",
        "model_type": training_request.model_type,
        "products_processed": len(products),
        "training_timestamp": datetime.utcnow().isoformat(),
        "message": "Model retraining completed successfully (placeholder implementation)"
    }


@router.get("/predictions")
async def get_recent_predictions(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    prediction_type: Optional[str] = Query(None, description="Filter by prediction type"),
    limit: int = Query(50, ge=1, le=500),
    session: Session = Depends(get_session)
):
    """
    Get recent ML predictions and their accuracy.
    
    Args:
        store_id: Optional store ID filter
        prediction_type: Optional prediction type filter
        limit: Maximum number of predictions to return
        session: Database session
    
    Returns:
        List[dict]: Recent predictions with metadata
    """
    query = select(MLPrediction).order_by(MLPrediction.prediction_date.desc())
    
    if store_id:
        query = query.where(MLPrediction.store_id == store_id)
    
    if prediction_type:
        query = query.where(MLPrediction.prediction_type == prediction_type)
    
    query = query.limit(limit)
    predictions = session.exec(query).all()
    
    results = []
    for pred in predictions:
        results.append({
            "id": pred.id,
            "product_id": pred.product_id,
            "store_id": pred.store_id,
            "prediction_type": pred.prediction_type,
            "predicted_value": pred.predicted_value,
            "confidence_score": pred.confidence_score,
            "prediction_date": pred.prediction_date.isoformat(),
            "target_date": pred.target_date.isoformat(),
            "model_version": pred.model_version
        })
    
    return {
        "predictions": results,
        "total_count": len(results)
    }
