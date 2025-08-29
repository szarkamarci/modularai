"""
Analytics page for the ModularAI Grocery Store demo.

Provides detailed analytics and visualizations for business intelligence.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

API_BASE_URL = "http://localhost:8000/api/v1"

def make_api_request(endpoint, method="GET", data=None):
    """Make API request to the FastAPI backend."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def main():
    st.title("📊 Business Analytics Dashboard")
    
    # Check API connection
    health = make_api_request("/../../health")
    if not health:
        st.error("API connection failed. Please ensure the FastAPI server is running.")
        return
    
    # Get products data
    products = make_api_request("/products/")
    if not products:
        return
    
    df = pd.DataFrame(products)
    
    # Key metrics
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_products = len(df)
        st.metric("Total Products", total_products)
    
    with col2:
        avg_price = df['price_dollars'].mean()
        st.metric("Average Price", f"${avg_price:.2f}")
    
    with col3:
        total_inventory_value = (df['stock_level'] * df['price_dollars']).sum()
        st.metric("Total Inventory Value", f"${total_inventory_value:.2f}")
    
    with col4:
        low_stock_items = df[df['is_low_stock'] == True]
        st.metric("Low Stock Items", len(low_stock_items))
    
    # Category analysis
    st.subheader("Category Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Products by category
        category_counts = df['category'].value_counts()
        fig_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Products by Category"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Average price by category
        avg_price_by_category = df.groupby('category')['price_dollars'].mean().sort_values(ascending=False)
        fig_bar = px.bar(
            x=avg_price_by_category.index,
            y=avg_price_by_category.values,
            title="Average Price by Category",
            labels={'x': 'Category', 'y': 'Average Price ($)'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Stock level analysis
    st.subheader("Stock Level Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Stock levels histogram
        fig_hist = px.histogram(
            df,
            x='stock_level',
            nbins=20,
            title="Stock Level Distribution",
            labels={'stock_level': 'Stock Level', 'count': 'Number of Products'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Stock vs Price scatter
        fig_scatter = px.scatter(
            df,
            x='stock_level',
            y='price_dollars',
            color='category',
            size='stock_level',
            title="Stock Level vs Price by Category",
            labels={'stock_level': 'Stock Level', 'price_dollars': 'Price ($)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Detailed product table
    st.subheader("Detailed Product Analysis")
    
    # Add calculated columns
    df['inventory_value'] = df['stock_level'] * df['price_dollars']
    df['stock_status'] = df.apply(
        lambda row: 'Critical' if row['stock_level'] <= row['min_stock_threshold'] * 0.5
        else 'Low' if row['is_low_stock']
        else 'Good', axis=1
    )
    
    # Display enhanced table
    st.dataframe(
        df[['name', 'category', 'price_dollars', 'stock_level', 'min_stock_threshold', 'inventory_value', 'stock_status']],
        column_config={
            'name': 'Product Name',
            'category': 'Category',
            'price_dollars': st.column_config.NumberColumn('Price ($)', format='$%.2f'),
            'stock_level': 'Stock Level',
            'min_stock_threshold': 'Min Threshold',
            'inventory_value': st.column_config.NumberColumn('Inventory Value ($)', format='$%.2f'),
            'stock_status': st.column_config.SelectboxColumn(
                'Stock Status',
                options=['Good', 'Low', 'Critical']
            )
        },
        use_container_width=True
    )

if __name__ == "__main__":
    main()
