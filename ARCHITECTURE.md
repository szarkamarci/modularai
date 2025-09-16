# ModularAI System Architecture

## 1. Project Overview

The ModularAI system is an AI-ready, scalable framework designed for building intelligent, domain-specific applications. Its core philosophy is to provide a reusable, modular platform that can be adapted to various business domains—such as manufacturing, financial markets, or logistics—by reconfiguring its core components.

To validate and demonstrate its capabilities, this instance of ModularAI is implemented as a real-world **Grocery Store AI System**. This application serves as a proof-of-concept, showcasing how the platform can solve complex, domain-specific problems.

### Core Objectives

The primary goals of the grocery store implementation are to:

-   **Optimize Inventory Management**: Minimize waste and carrying costs by maintaining optimal stock levels.
-   **Predict Demand and Stockouts**: Use historical data to forecast future product demand and proactively flag items at risk of stocking out.
-   **Provide Customer Personalization**: Enhance the customer experience through AI-powered chatbots for product queries and personalized recommendations.
-   **Support Store Managers**: Offer intuitive dashboards for monitoring key performance indicators (KPIs), viewing forecasts, and managing inventory.
-   **Enable Data Science Experimentation**: Create a flexible environment where data scientists can easily plug in, train, and test new machine learning models with minimal friction.

---

## 2. System Architecture (High-Level)

The system is built on a layered, microservices-oriented architecture. This design promotes separation of concerns, scalability, and maintainability. Each component is containerized and can be deployed independently.

### Architectural Diagram (Textual)

```
+-----------------------------------------------------------------+
|                         Frontend Layer                          |
|  (Nuxt 3 / Vue.js + Tailwind CSS)                               |
| +------------------+ +-------------------+ +------------------+ |
| | Customer Portal  | | Manager Dashboard | | DS Workbench     | |
| +------------------+ +-------------------+ +------------------+ |
+--------------------------------|--------------------------------+
                                 | (REST APIs / WebSockets)
+--------------------------------|--------------------------------+
|                         Backend Layer                           |
|  (FastAPI / Python)                                             |
| +------------------+ +-------------------+ +------------------+ |
| | API Gateway      | | Orchestration Svc | | AI/ML Services   | |
| +------------------+ +-------------------+ +------------------+ |
+--------------------------------|--------------------------------+
                                 | (Events / DB Calls)
+--------------------------------|--------------------------------+
|                       Data Infrastructure                       |
| +------------+ +-----------+ +---------+ +---------+ +---------+ |
| | PostgreSQL | | MongoDB   | | Redis   | | Kafka   | | VectorDB| |
| |(Timescale) | |(Documents)| |(Cache)  | |(Events) | |(pgvector)| |
| +------------+ +-----------+ +---------+ +---------+ +---------+ |
+-----------------------------------------------------------------+
|                        Deployment Layer                         |
|  +--------------------------+ +-------------------------------+ |
|  | Docker Compose (Dev/VM)  | | Kubernetes (Production)       | |
|  +--------------------------+ +-------------------------------+ |
+-----------------------------------------------------------------+
```

### Key Layers & Components

-   **Frontend Layer**:
    -   **Framework**: Nuxt 3 (a Vue.js framework) with Tailwind CSS for styling.
    -   **Portals**: Separate, purpose-built interfaces for different user roles (e.g., a customer-facing app, a manager's dashboard, and a data scientist's workbench).

-   **Backend Layer**:
    -   **Framework**: FastAPI (Python) for building high-performance, asynchronous APIs.
    -   **Services**: A collection of microservices, including an API Gateway, an orchestration service to manage workflows, and dedicated AI/ML services for model inference.

-   **Data Infrastructure**:
    -   **PostgreSQL**: The primary transactional database, enhanced with the **Timescale** extension for efficient time-series data handling (e.g., sales history).
    -   **MongoDB**: A document store for unstructured or semi-structured data, such as product metadata or user profiles.
    -   **Redis**: An in-memory data store used for caching, session management, and as a high-speed message broker.
    -   **Apache Kafka**: A distributed event streaming platform for ingesting and processing real-time data, such as transactions and user interactions.
    -   **Vector Database**: PostgreSQL with the `pgvector` extension is used for storing and querying high-dimensional embeddings for the RAG system.

-   **AI/ML Layer**:
    -   **Model Training Pipelines**: Scripts and services for training models like demand forecasters, stock-out predictors, and personalization engines.
    -   **RAG Components**: The system for Retrieval-Augmented Generation, which includes embedding models and a vector search mechanism for the product chatbot.

-   **Admin Layer** (Optional):
    -   A pre-built admin panel like **Laravel Nova** or a custom solution can be integrated for rapid development of internal management tools and dashboards.

-   **Deployment**:
    -   **Docker Compose**: Used for local development and simple, single-VM deployments.
    -   **Kubernetes**: The preferred solution for production environments, providing container orchestration, scalability, and resilience.

---

## 3. Data Flow

The data flow is designed to be event-driven and scalable, ensuring real-time processing and responsiveness.

1.  **VM/Docker Startup**: Services are bootstrapped via Docker Compose (for development) or Kubernetes (for production). Service discovery and networking are handled by the container orchestrator.

2.  **Configuration Loading**: On startup, each service loads its configuration from environment variables, which are populated from `.env` files (dev) or a secrets manager (prod).

3.  **Database Connection**: Backend services establish connection pools to PostgreSQL and MongoDB, ensuring efficient and persistent database access.

4.  **Event Ingestion**: Real-time events, such as customer transactions or product views, are captured and streamed into **Kafka** topics. This decouples data producers from consumers.

5.  **Data Storage & Processing**:
    -   Kafka consumers process the event streams, normalizing and storing data in **PostgreSQL** (e.g., `transactions`, `inventory` tables) and the vector database (`product_embeddings`).
    -   Time-series data (e.g., sales per hour) is written to hyper-tables managed by **TimescaleDB**.

6.  **Model Execution**: AI services consume data from Kafka topics or query the databases directly. They generate insights (e.g., demand forecasts, stockout alerts) and push the results back to the backend, either via an API call or by producing a message to another Kafka topic.

7.  **Frontend Consumption**: The Nuxt frontend application queries the FastAPI backend to fetch data for dashboards, chatbot responses, or personalized product recommendations. Real-time updates can be pushed to the client using WebSockets.

---

## 4. Database Design

The database schema is designed to be normalized and efficient, with clear separation of concerns.

### Example Core Tables (PostgreSQL)

-   `products`: Stores product information.
    -   `id` (PK), `name`, `description`, `category`, `manufacturer`, `embedding` (vector).
-   `transactions`: Records all sales transactions.
    -   `id` (PK), `product_id` (FK), `user_id` (FK), `timestamp`, `quantity`, `price`.
-   `inventory`: Tracks stock levels for each product.
    -   `product_id` (PK, FK), `stock_level`, `reorder_threshold`.
-   `recent_product_views`: Stores user interaction data for personalization.
    -   `id` (PK), `user_id` (FK), `product_id` (FK), `viewed_at` (timestamp).

### Managing the Database

-   **Creating a New Table**: Database schema changes are managed through migration scripts (e.g., using Alembic). This ensures that changes are version-controlled and can be applied consistently across different environments.
-   **Inserting/Uploading Data**: Data is ingested into the database through ETL (Extract, Transform, Load) pipelines for batch data or via Kafka consumers for real-time event streams.

---

## 5. Model Lifecycle

The model lifecycle is managed to ensure reproducibility, versioning, and seamless deployment.

1.  **Model Registration**: Trained models are registered in a model registry (e.g., MLflow or a custom service). The registry stores model artifacts, versions, and metadata (e.g., training metrics, parameters).

2.  **Training Pipelines**: Training pipelines are automated scripts that:
    -   Fetch data from the database or a data lake.
    -   Preprocess and transform the data.
    -   Train the model.
    -   Evaluate its performance.
    -   Store the trained model artifact in the registry.

3.  **Model Deployment**: Models are deployed in one of two ways:
    -   **Microservices**: Deployed as independent services with their own FastAPI endpoints for real-time inference.
    -   **Batch Jobs**: Triggered by events (e.g., a new day's sales data arriving) or run on a schedule to generate predictions in batch.

### Model Examples

-   **Demand Forecasting**: An LSTM or Prophet model trained on historical sales time-series data.
-   **Stockout Prediction**: A Random Forest or XGBoost model trained on inventory levels, sales velocity, and seasonality.
-   **Personalization**: Collaborative filtering algorithms or embedding-based models for product recommendations.
-   **Chatbot/RAG**: An LLM combined with product embeddings to answer customer questions.

---

## 6. Configuration & Secrets

Configuration and secrets are managed securely and separately from the codebase.

-   **Development**: In local development, configurations are loaded from `.env` files at the root of the project.
-   **Production**: In production, secrets are injected into the environment using a secrets manager like **HashiCorp Vault**, **Doppler**, or native solutions like **Docker secrets** or **Kubernetes Secrets**.

### Required Configurations

-   Database credentials (username, password, host, port).
-   Kafka broker addresses.
-   API keys for any external integrations (e.g., payment gateways, supplier APIs).

---

## 7. Deployment

The system is designed for containerized deployment to ensure consistency across environments.

-   **VM-Based Deployment**: For simpler setups, the entire system can be deployed on a single virtual machine using **Docker Compose**. This is suitable for small-scale applications or internal testing.
-   **Docker/Kubernetes Deployment**: For production, services are deployed as containers in a **Kubernetes** cluster. Kubernetes manages networking, scaling, and service discovery, providing a robust and resilient environment.
-   **CI/CD Pipelines**: Automated CI/CD pipelines (e.g., using GitHub Actions or Jenkins) are used to build, test, and deploy updates to the services, ensuring a streamlined and reliable release process.

---

## 8. Extensibility

The modular architecture is designed for easy extension and integration.

-   **Plugging in New Modules/Models**: A new AI model can be added by creating a new microservice with a FastAPI endpoint and registering it with the API Gateway. The frontend can then be updated to consume the new service.
-   **External System Integration**: The system can integrate with external systems, such as a Point-of-Sale (POS) system or supplier APIs, by creating dedicated services that communicate with them and produce events into the Kafka stream.
-   **Multi-Store Scaling**: The platform supports multi-store deployments by partitioning data by `store_id`. A central core can manage shared resources, while each store operates on its own data partition.

---

## 9. Future Directions

The ModularAI platform is designed to evolve with advancements in AI and data engineering.

-   **Reinforcement Learning (RL)**: Implementing RL-based agents for dynamic inventory optimization.
-   **Real-time Customer Personalization**: Enhancing the personalization engine to react to customer actions in real-time.
-   **Serverless Inference**: Migrating model inference endpoints to serverless platforms for cost-effective, auto-scaling performance.
-   **Federated Learning**: Training models across multiple stores without centralizing sensitive data, improving model accuracy while preserving privacy.
