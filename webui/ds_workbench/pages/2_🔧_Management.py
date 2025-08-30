"""
Management page for the ModularAI Grocery Store demo.

Provides inventory management tools and operational controls.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Management", page_icon="🔧", layout="wide")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000") + "/api/v1"

def make_api_request(endpoint, method="GET", data=None):
    """Make API request to the FastAPI backend."""
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
        st.error("Cannot connect to API. Make sure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def main():
    st.title("🔧 Inventory Management")
    
    # Check API connection
    health = make_api_request("/../../health")
    if not health:
        st.error("API connection failed. Please ensure the FastAPI server is running.")
        return
    
    # Tabs for different management functions
    tab1, tab2, tab3 = st.tabs(["📦 Stock Management", "➕ Add Product", "📝 Bulk Operations"])
    
    with tab1:
        st.subheader("Stock Level Management")
        
        # Get products
        products = make_api_request("/products/")
        if not products:
            return
        
        # Product selection for stock adjustment
        product_options = {f"{p['name']} (Current: {p['stock_level']})": p for p in products}
        selected_product_key = st.selectbox("Select Product", list(product_options.keys()))
        
        if selected_product_key:
            selected_product = product_options[selected_product_key]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Stock", selected_product['stock_level'])
            
            with col2:
                st.metric("Min Threshold", selected_product['min_stock_threshold'])
            
            with col3:
                st.metric("Price", f"${selected_product['price_dollars']:.2f}")
            
            # Stock adjustment form
            st.markdown("**Adjust Stock Level:**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                adjustment_qty = st.number_input(
                    "Adjustment Quantity",
                    min_value=-selected_product['stock_level'],
                    value=0,
                    help="Positive for restock, negative for removal"
                )
            
            with col2:
                reason = st.selectbox(
                    "Reason",
                    ["restock", "sale", "damage", "expired", "manual_adjustment"]
                )
            
            with col3:
                st.write("")  # Spacing
                if st.button("Apply Adjustment", type="primary"):
                    if adjustment_qty != 0:
                        adjustment_data = {
                            "product_id": selected_product['id'],
                            "adjustment_quantity": adjustment_qty,
                            "reason": reason
                        }
                        
                        result = make_api_request("/inventory/adjust", "POST", adjustment_data)
                        if result:
                            st.success(f"✅ Stock adjusted! New level: {result['new_stock']}")
                            st.rerun()
                    else:
                        st.warning("Please enter a non-zero adjustment quantity.")
        
        # Stock movements history
        if selected_product_key:
            st.markdown("**Recent Stock Movements:**")
            movements = make_api_request(f"/inventory/movements/{selected_product['id']}")
            
            if movements and movements.get('movements'):
                movements_df = pd.DataFrame(movements['movements'])
                movements_df['timestamp'] = pd.to_datetime(movements_df['timestamp'])
                movements_df = movements_df.sort_values('timestamp', ascending=False)
                
                st.dataframe(
                    movements_df[['timestamp', 'quantity', 'transaction_type', 'total_amount_dollars']],
                    column_config={
                        'timestamp': st.column_config.DatetimeColumn('Date/Time'),
                        'quantity': 'Quantity',
                        'transaction_type': 'Type',
                        'total_amount_dollars': st.column_config.NumberColumn('Amount ($)', format='$%.2f')
                    },
                    use_container_width=True
                )
            else:
                st.info("No stock movements found for this product.")
    
    with tab2:
        st.subheader("Add New Product")
        
        # Get stores for dropdown
        # For demo purposes, we'll use hardcoded store options
        store_options = {"Store 1": 1, "Store 2": 2}
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Product Name*")
                category = st.selectbox("Category*", ["Produce", "Dairy", "Bakery", "Beverages", "Meat", "Frozen", "Other"])
                price = st.number_input("Price ($)*", min_value=0.01, value=1.00, step=0.01)
            
            with col2:
                store = st.selectbox("Store*", list(store_options.keys()))
                stock_level = st.number_input("Initial Stock Level", min_value=0, value=0)
                min_threshold = st.number_input("Minimum Stock Threshold", min_value=0, value=10)
            
            description = st.text_area("Product Description")
            
            submitted = st.form_submit_button("Add Product", type="primary")
            
            if submitted:
                if product_name and category and price > 0:
                    product_data = {
                        "name": product_name,
                        "category": category,
                        "price": int(price * 100),  # Convert to cents
                        "stock_level": stock_level,
                        "min_stock_threshold": min_threshold,
                        "store_id": store_options[store],
                        "description": description if description else None
                    }
                    
                    result = make_api_request("/products/", "POST", product_data)
                    if result:
                        st.success(f"✅ Product '{product_name}' added successfully!")
                        st.rerun()
                else:
                    st.error("Please fill in all required fields (marked with *).")
    
    with tab3:
        st.subheader("Bulk Operations")
        
        # Bulk stock adjustment
        st.markdown("**Bulk Stock Adjustment by Category:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bulk_category = st.selectbox("Category", ["Produce", "Dairy", "Bakery", "Beverages", "All Categories"])
        
        with col2:
            bulk_adjustment = st.number_input("Adjustment Amount", value=0)
        
        with col3:
            bulk_reason = st.selectbox("Reason", ["restock", "inventory_count", "bulk_adjustment"])
        
        if st.button("Apply Bulk Adjustment", type="secondary"):
            if bulk_adjustment != 0:
                # Get products to adjust
                if bulk_category == "All Categories":
                    products_to_adjust = make_api_request("/products/")
                else:
                    products_to_adjust = make_api_request(f"/products/?category={bulk_category}")
                
                if products_to_adjust:
                    success_count = 0
                    error_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, product in enumerate(products_to_adjust):
                        status_text.text(f"Adjusting {product['name']}...")
                        
                        adjustment_data = {
                            "product_id": product['id'],
                            "adjustment_quantity": bulk_adjustment,
                            "reason": bulk_reason
                        }
                        
                        result = make_api_request("/inventory/adjust", "POST", adjustment_data)
                        if result:
                            success_count += 1
                        else:
                            error_count += 1
                        
                        progress_bar.progress((i + 1) / len(products_to_adjust))
                    
                    status_text.text("Bulk adjustment completed!")
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully adjusted {success_count} products")
                    if error_count > 0:
                        st.error(f"❌ Failed to adjust {error_count} products")
            else:
                st.warning("Please enter a non-zero adjustment amount.")
        
        # Low stock restock suggestions
        st.markdown("**Low Stock Restock Suggestions:**")
        
        alerts = make_api_request("/inventory/alerts")
        if alerts:
            if alerts:
                st.warning(f"⚠️ {len(alerts)} products need attention")
                
                # Create restock suggestions
                restock_df = pd.DataFrame(alerts)
                restock_df['suggested_restock'] = restock_df['min_threshold'] * 2 - restock_df['current_stock']
                restock_df['suggested_restock'] = restock_df['suggested_restock'].clip(lower=0)
                
                st.dataframe(
                    restock_df[['product_name', 'category', 'current_stock', 'min_threshold', 'suggested_restock']],
                    column_config={
                        'product_name': 'Product',
                        'category': 'Category',
                        'current_stock': 'Current Stock',
                        'min_threshold': 'Min Threshold',
                        'suggested_restock': 'Suggested Restock'
                    },
                    use_container_width=True
                )
            else:
                st.success("🎉 All products are adequately stocked!")

if __name__ == "__main__":
    main()
