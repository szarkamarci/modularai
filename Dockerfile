# Multi-stage Dockerfile for ModularAI Grocery Store System
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# FastAPI service
FROM base as api
EXPOSE 8000
CMD ["python", "-m", "domain_services.grocery.main"]

# Streamlit service
FROM base as streamlit
EXPOSE 8501
CMD ["streamlit", "run", "webui/ds_workbench/streamlit_app.py", "--server.address", "0.0.0.0"]
