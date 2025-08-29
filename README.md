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

```bash
# 1. Setup environment
cp .env.example .env  # Configure Supabase credentials

# 2. Start services
docker-compose up -d

# 3. Initialize database
python -m core_services.database.init_db

# 4. Access applications
# Manager Dashboard: http://localhost:3000
# API Docs: http://localhost:8000/docs
# ML Workbench: http://localhost:8501
```

## API Endpoints

- `GET /products` - List products with stock levels
- `POST /products/{id}/forecast` - Get demand predictions
- `GET /inventory/alerts` - Current stockout warnings  
- `POST /chat` - RAG chatbot for product queries
- `POST /ml/retrain` - Trigger model retraining

## Development Roadmap

✅ **Implemented so far:**
- Core project structure and Docker setup
- Basic FastAPI routes and SQLModel schemas
- Vue 3 dashboard foundation

🚀 **Next Priorities (good starting points for AI-assisted dev in Windsurf):**
- Supabase database integration
- Demand forecasting pipeline
- RAG chatbot implementation
- Manager dashboard completion