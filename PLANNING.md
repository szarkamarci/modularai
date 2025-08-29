# PLANNING.md

## 🎯 Purpose & Vision
The goal of this project is to build **ModularAI - Grocery Store AI System**, a reusable framework that can scale into other domains (factories, hotels, stock market, etc.).  
This document provides the **source of truth** for architectural decisions, constraints, and the development approach.  
When working with an AI assistant (e.g., Claude in Windsurf, ChatGPT, local LLMs), always **reference this file first** in a new conversation:  
> “Use the structure and decisions outlined in PLANNING.md.”

---

## 🏗️ High-Level Architecture
- **Core Services**: Database, authentication, RAG, shared infrastructure.  
- **Domain Services**: Grocery-specific business logic (FastAPI routes, ML pipelines).  
- **WebUI**:  
  - Manager Dashboard (Vue 3 + Tailwind)  
  - Data Science Workbench (Streamlit)  
- **Infra**: Docker Compose for orchestration, environment setup.

### Data Flow
1. **Transactions** flow into Supabase (Postgres + Realtime).  
2. **Pipelines** (demand forecasting, stockout prediction) consume fresh data.  
3. **RAG** stores product embeddings → enables chatbot and semantic search.  
4. **Dashboards** expose insights to store managers and data scientists.

---

## ⚙️ Tech Stack
- **Backend**: FastAPI + SQLModel  
- **Database**: Supabase (PostgreSQL with Auth & Realtime)  
- **Frontend**: Vue 3 + Tailwind CSS  
- **ML / AI**: PyTorch, scikit-learn, sentence-transformers  
- **RAG**: Local LLM (Ollama/Llama 2, expandable to Qwen, GPT-4o, Claude)  
- **Infra**: Docker Compose, optional MCP servers for tool access  

---

## 📦 Tools & Development Workflow
- **Claude in Windsurf** → repo-aware coding, cross-file reasoning.  
- **ChatGPT / GPT-4o** → long structured reasoning, design docs, fallback memory.  
- **Local LLMs (Ollama)** → private experiments, embeddings, offline tasks.  
- **Supabase MCP** → allow AI to query/store directly in Postgres.  
- **Filesystem MCP** → safe file navigation for repo-aware AI.  

**Workflow:**  
1. Reference `PLANNING.md` at the start of an AI session.  
2. Use Windsurf for implementation/refactors.  
3. Use ChatGPT/Claude for higher-level design.  
4. Commit changes incrementally, keep documentation updated.

---

## 🚧 Constraints & Priorities
- **Must be modular**: architecture should allow swapping domains.  
- **MVP focus**: grocery store pipeline must work end-to-end (transactions → forecasts → dashboard).  
- **AI-native dev**: assume much of the coding will be AI-assisted.  
- **Security**: database access must be scoped, role-based, and safe.  
- **Scalability**: design for growth but optimize for rapid iteration first.

---

## 📌 Next Steps (for AI & Human devs)
1. Finalize Supabase integration (tables, realtime sync).  
2. Implement demand forecasting ML pipeline.  
3. Add stockout alert mechanism.  
4. RAG chatbot prototype using embeddings.  
5. Expand Manager Dashboard with predictions and alerts.  

---

_End of PLANNING.md – always reference this document when starting new work._
