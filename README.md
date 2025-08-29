# ModularAI - Grocery Store AI System

A scalable, domain-adaptable AI framework for intelligent retail systems. This instance implements a full-stack grocery store solution with predictive analytics, RAG chatbots, and microservices architecture.

## Architecture

```
modularai/
├── core_services/           # Shared infrastructure
│   ├── database/           # DB connection & models
│   ├── auth/               # Authentication service
│   └── rag/                # RAG embedding & retrieval
├── domain_services/
│   └── grocery/            # Grocery business logic
│       ├── api/            # FastAPI routes
│       ├── models/         # SQLModel schemas
│       ├── ml_pipelines/   # Demand forecasting, inventory prediction
│       └── main.py         # Service entrypoint
├── webui/
│   ├── manager_dashboard/  # Vue 3 admin interface
│   └── ds_workbench/      # Streamlit ML interface
└── infra/
    └── docker-compose.yml  # Container setup
```

## Tech Stack

- **Backend**: FastAPI + SQLModel
- **Database**: Supabase (PostgreSQL + Auth + Realtime)
- **Frontend**: Vue 3 + Tailwind CSS
- **ML**: PyTorch, scikit-learn, sentence-transformers
- **RAG**: Local LLM + vector embeddings
- **Deploy**: Docker Compose

## Key Features

**For Store Managers:**
- Inventory dashboard with stock levels and forecasts
- Automated stockout alerts and demand predictions
- Role-based access per store location

**For Data Scientists:**  
- Plug-and-play ML pipelines for demand forecasting
- Real-time transaction data access
- Model experiment tracking

**For Customers:**
- RAG-powered product chatbot
- Semantic product search using embeddings

## Core Models & Data Flow

**Database Models (SQLModel):**
- `Product`: id, name, category, price, stock_level, embeddings
- `Transaction`: id, product_id, quantity, timestamp, store_id
- `Store`: id, name, location, manager_id
- `User`: id, email, role, store_id

**ML Pipelines:**
- Demand forecasting: Historical transactions → Future demand predictions
- Stockout prediction: Current inventory + demand → Alert triggers
- Product embeddings: Product descriptions → Vector representations

**RAG System:**
- Product catalog → Sentence transformer embeddings → Vector store
- User query → Embedding → Similarity search → LLM response

## Environment Setup

```bash
# Required environment variables
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
DATABASE_URL=your_supabase_postgres_url

# ML Models
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=ollama/llama2

# API Config
API_HOST=0.0.0.0
API_PORT=8000
```

## Quick Start

### 🐳 Docker (Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd plutusai

# 2. Start all services with Docker Compose
cd infra
docker-compose up -d

# 3. Initialize database (one-time setup)
docker-compose exec grocery-api python -m core_services.database.init_db

# 4. Access applications
# FastAPI Backend: http://localhost:8000
# API Documentation: http://localhost:8000/docs
# Streamlit Demo: http://localhost:8501
# PostgreSQL: localhost:54322
```

### 🔧 Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment variables
cp .env.example .env

# 3. Start Supabase locally (optional)
supabase start

# 4. Initialize database
python -m core_services.database.init_db

# 5. Start services
# FastAPI Backend
python -m domain_services.grocery.main

# Streamlit Frontend (in another terminal)
streamlit run webui/ds_workbench/streamlit_app.py
```

## API Endpoints

- `GET /products` - List products with stock levels
- `POST /products/{id}/forecast` - Get demand predictions
- `GET /inventory/alerts` - Current stockout warnings  
- `POST /chat` - RAG chatbot for product queries
- `POST /ml/retrain` - Trigger model retraining

## 🐳 Docker Deployment

### Production Deployment
```bash
# Build and start all services
docker-compose -f infra/docker-compose.yml up -d --build

# View logs
docker-compose -f infra/docker-compose.yml logs -f

# Stop services
docker-compose -f infra/docker-compose.yml down
```

### Service Architecture
- **grocery-api**: FastAPI backend (port 8000)
- **ds-workbench**: Streamlit frontend (port 8501)  
- **postgres**: PostgreSQL database (port 54322)
- **manager-dashboard**: Vue.js UI (port 3000) *[planned]*

### Environment Variables
Copy `.env.example` to `.env` and customize:
- Database credentials
- Supabase configuration
- ML model settings

## Development Roadmap

✅ **Completed:**
- Complete FastAPI backend with SQLModel ORM
- PostgreSQL database with sample data
- Comprehensive API endpoints (products, inventory, chat, ML)
- Streamlit demo frontend with interactive dashboard
- Docker containerization for all services
- Unit tests with 100% pass rate
- Git repository initialization

🚀 **Next Priorities:**
- Vue.js Manager Dashboard UI
- Advanced ML demand forecasting
- RAG chatbot with vector embeddings
- Real-time notifications
- Authentication & authorization
- Manager dashboard completion