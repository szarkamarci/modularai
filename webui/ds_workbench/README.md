# ModularAI Grocery Store - Streamlit Demo Frontend

A comprehensive demo interface showcasing the grocery store AI system capabilities.

## Features

- **Dashboard**: Real-time inventory overview with key metrics
- **Product Catalog**: Interactive product browsing with filtering
- **Stock Alerts**: Automated low stock warnings and management
- **Demand Forecasting**: ML-powered demand predictions
- **AI Assistant**: RAG chatbot for product queries
- **Analytics**: Business intelligence and visualizations
- **Management**: Inventory management tools and bulk operations

## Running the Demo

1. Ensure the FastAPI backend is running:
   ```bash
   python -m domain_services.grocery.main
   ```

2. Start the Streamlit frontend:
   ```bash
   streamlit run webui/ds_workbench/streamlit_app.py
   ```

3. Access the demo at: http://localhost:8501

## Pages

- **Main Dashboard**: Overview and navigation
- **📊 Analytics**: Detailed business analytics and charts
- **🔧 Management**: Inventory management and bulk operations

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000/api/v1` and provides a user-friendly interface for all system capabilities.
