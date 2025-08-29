"""
ModularAI Grocery Store - Streamlit Demo Frontend

A comprehensive demo interface showcasing the grocery store AI system capabilities
including inventory management, demand forecasting, and RAG chatbot.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="ModularAI Grocery Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint, method="GET", data=None):
    """
    Make API request to the FastAPI backend.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request data for POST/PUT requests
    
    Returns:
        Response data or None if error
    """
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def display_inventory_overview():
    """Display inventory overview dashboard."""
    st.subheader("📊 Inventory Overview")
    
    # Get inventory status
    status = make_api_request("/inventory/status")
    if not status:
        return
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Products",
            value=status["total_products"]
        )
    
    with col2:
        st.metric(
            label="Low Stock Items",
            value=status["low_stock_count"],
            delta=f"-{status['low_stock_count']}" if status["low_stock_count"] > 0 else "0"
        )
    
    with col3:
        st.metric(
            label="Out of Stock",
            value=status["out_of_stock_count"],
            delta=f"-{status['out_of_stock_count']}" if status["out_of_stock_count"] > 0 else "0"
        )
    
    with col4:
        st.metric(
            label="Total Inventory Value",
            value=f"${status['total_value_dollars']:.2f}"
        )

def display_products_table():
    """Display products table with filtering options."""
    st.subheader("🛍️ Product Catalog")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        store_filter = st.selectbox("Filter by Store", ["All Stores", "Store 1", "Store 2"])
    
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All Categories", "Produce", "Dairy", "Bakery", "Beverages"])
    
    with col3:
        low_stock_only = st.checkbox("Show Low Stock Only")
    
    # Build API parameters
    params = {}
    if store_filter != "All Stores":
        params["store_id"] = 1 if store_filter == "Store 1" else 2
    if category_filter != "All Categories":
        params["category"] = category_filter
    if low_stock_only:
        params["low_stock_only"] = True
    
    # Build query string
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    endpoint = f"/products/?{query_string}" if query_string else "/products/"
    
    # Get products
    products = make_api_request(endpoint)
    if not products:
        return
    
    if not products:
        st.info("No products found matching the selected filters.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(products)
    
    # Display table
    st.dataframe(
        df[["name", "category", "price_dollars", "stock_level", "min_stock_threshold", "is_low_stock"]],
        column_config={
            "name": "Product Name",
            "category": "Category",
            "price_dollars": st.column_config.NumberColumn("Price ($)", format="$%.2f"),
            "stock_level": "Stock Level",
            "min_stock_threshold": "Min Threshold",
            "is_low_stock": st.column_config.CheckboxColumn("Low Stock")
        },
        use_container_width=True
    )
    
    # Stock level visualization
    if len(df) > 0:
        fig = px.bar(
            df, 
            x="name", 
            y="stock_level",
            color="is_low_stock",
            title="Stock Levels by Product",
            color_discrete_map={True: "#ff7f0e", False: "#1f77b4"}
        )
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

def display_stock_alerts():
    """Display stock alerts and warnings."""
    st.subheader("⚠️ Stock Alerts")
    
    alerts = make_api_request("/inventory/alerts")
    if not alerts:
        return
    
    if not alerts:
        st.success("🎉 No stock alerts! All products are adequately stocked.")
        return
    
    # Display alerts
    for alert in alerts:
        with st.expander(f"🚨 {alert['product_name']} - {alert['category']}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Stock", alert["current_stock"])
            
            with col2:
                st.metric("Min Threshold", alert["min_threshold"])
            
            with col3:
                if alert.get("days_until_stockout"):
                    st.metric("Days Until Stockout", f"{alert['days_until_stockout']} days")
                else:
                    st.metric("Days Until Stockout", "Unknown")
            
            # Stock adjustment
            st.write("**Quick Stock Adjustment:**")
            adjustment_col1, adjustment_col2 = st.columns(2)
            
            with adjustment_col1:
                adjustment_qty = st.number_input(
                    "Adjustment Quantity",
                    min_value=-alert["current_stock"],
                    value=20,
                    key=f"adj_{alert['product_id']}"
                )
            
            with adjustment_col2:
                if st.button(f"Adjust Stock", key=f"btn_{alert['product_id']}"):
                    adjustment_data = {
                        "product_id": alert["product_id"],
                        "adjustment_quantity": adjustment_qty,
                        "reason": "manual_adjustment_via_demo"
                    }
                    
                    result = make_api_request("/inventory/adjust", "POST", adjustment_data)
                    if result:
                        st.success(f"✅ Stock adjusted! New level: {result['new_stock']}")
                        st.rerun()

def display_demand_forecasting():
    """Display demand forecasting interface."""
    st.subheader("📈 Demand Forecasting")
    
    # Get products for selection
    products = make_api_request("/products/")
    if not products:
        return
    
    # Product selection
    product_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in products}
    selected_product = st.selectbox("Select Product for Forecasting", list(product_options.keys()))
    
    if not selected_product:
        return
    
    product_id = product_options[selected_product]
    
    # Forecasting parameters
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_days = st.slider("Forecast Period (days)", 1, 30, 7)
    
    with col2:
        confidence_level = st.slider("Confidence Level", 0.8, 0.99, 0.95)
    
    if st.button("Generate Forecast"):
        forecast_data = {
            "product_id": product_id,
            "days_ahead": forecast_days,
            "confidence_level": confidence_level
        }
        
        forecast = make_api_request(f"/ml/{product_id}/forecast", "POST", forecast_data)
        
        if forecast:
            # Display forecast results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Predicted Demand", f"{forecast['predicted_demand']:.1f} units")
            
            with col2:
                st.metric("Confidence Score", f"{forecast['confidence_score']:.2%}")
            
            with col3:
                st.metric("Historical Average", f"{forecast['historical_avg']:.1f} units/day")
            
            # Recommendation
            st.markdown("**Recommendation:**")
            st.info(forecast["recommendation"])
            
            # Create forecast visualization
            current_date = datetime.now()
            dates = [current_date + timedelta(days=i) for i in range(forecast_days + 1)]
            
            # Simulate daily breakdown (in real implementation, this would come from the ML model)
            daily_forecast = [forecast["historical_avg"] * (1 + 0.1 * (i % 3 - 1)) for i in range(forecast_days + 1)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=daily_forecast,
                mode='lines+markers',
                name='Predicted Demand',
                line=dict(color='#1f77b4')
            ))
            
            fig.update_layout(
                title=f"Demand Forecast for {forecast['product_name']}",
                xaxis_title="Date",
                yaxis_title="Predicted Units",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_chat_interface():
    """Display RAG chatbot interface."""
    st.subheader("🤖 AI Product Assistant")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display relevant products if available
            if message["role"] == "assistant" and "products" in message:
                if message["products"]:
                    st.write("**Relevant Products:**")
                    for product in message["products"]:
                        st.write(f"• **{product['name']}** ({product['category']}) - ${product['price_dollars']:.2f} - Stock: {product['stock_level']}")
    
    # Chat input
    if prompt := st.chat_input("Ask about products, inventory, or get recommendations..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        chat_data = {"message": prompt}
        response = make_api_request("/chat/", "POST", chat_data)
        
        if response:
            # Add assistant message
            assistant_message = {
                "role": "assistant", 
                "content": response["response"],
                "products": response.get("relevant_products", [])
            }
            st.session_state.messages.append(assistant_message)
            
            with st.chat_message("assistant"):
                st.markdown(response["response"])
                
                # Display relevant products
                if response.get("relevant_products"):
                    st.write("**Relevant Products:**")
                    for product in response["relevant_products"]:
                        st.write(f"• **{product['name']}** ({product['category']}) - ${product['price_dollars']:.2f} - Stock: {product['stock_level']}")

def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🛒 ModularAI Grocery Store Demo</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Dashboard", "Product Catalog", "Stock Alerts", "Demand Forecasting", "AI Assistant"]
    )
    
    # API Health Check
    health = make_api_request("/../../health")
    if health:
        st.sidebar.success(f"✅ API Connected - {health['service']} v{health['version']}")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.error("Please ensure the FastAPI server is running: `python -m domain_services.grocery.main`")
        return
    
    # Page routing
    if page == "Dashboard":
        st.markdown("### 📊 Real-time Inventory Dashboard")
        display_inventory_overview()
        
        st.markdown("---")
        
        # Recent activity simulation
        st.subheader("📈 Recent Activity")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🔄 Last sync: " + datetime.now().strftime("%H:%M:%S"))
        
        with col2:
            if st.button("🔄 Refresh Data"):
                st.rerun()
    
    elif page == "Product Catalog":
        display_products_table()
    
    elif page == "Stock Alerts":
        display_stock_alerts()
    
    elif page == "Demand Forecasting":
        display_demand_forecasting()
    
    elif page == "AI Assistant":
        display_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**ModularAI Grocery Store System** | Built with FastAPI, SQLModel, and Streamlit | "
        "[API Documentation](http://localhost:8000/docs)"
    )

if __name__ == "__main__":
    main()
