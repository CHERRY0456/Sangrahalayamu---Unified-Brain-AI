# IndustryBrain-AI: Enterprise Python Backend

This is the backend API and AI reasoning engine for IndustryBrain-AI. It is built with FastAPI, PostgreSQL, Neo4j, Qdrant, and AWS Bedrock (Qwen).

---

## 🛠️ Architecture and Services

The backend follows a service-oriented architecture with clean separation between controllers (routers) and business/AI logic (services).

### Key Modules:
- **`app/api/`**: Decoupled HTTP and SSE endpoints (no business logic in routers).
- **`app/core/`**: Centralized configuration management using Pydantic Settings (`settings.database.url`, `settings.aws.region`, etc.).
- **`app/services/`**:
  - **`processing/`**: Layout-aware parsing, OCR pipeline, chunking, and relationship generation.
  - **`retrieval/`**: Hybrid retrieval engine integrating vector similarity (Qdrant) and graph database queries (Neo4j) with weighted rank fusion.
  - **`llm/`**: AWS Bedrock providers and streaming client wrapper.
  - **`orchestrator/`**: Main orchestrator managing Specialized Agents (RCA, Safety, Recommendation) and assembling explainable context blocks.
  - **`graph/`**: Async Neo4j graph constructor and query engine.
  - **`audit/` & `transparency/`**: Diagnostic logging, provenance checks, and trace explanations.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
Create a virtual environment and install packages:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Unix/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the `.env.example` file and configure your Postgres, Neo4j, Qdrant, and AWS Bedrock credentials:
```bash
cp .env.example .env
```
Ensure you have values filled for:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- `QDRANT_URL`, `QDRANT_API_KEY`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`

### 3. Run the Database Seeder
Seed database roles, metadata schemas, and employee profiles:
```bash
python scripts/seed_users.py
```
*Note: This script automatically builds Postgres schemas if they do not exist.*

### 4. Run the API Server
Start the Uvicorn development server:
```bash
uvicorn app.main:app --reload --port 8000
```
Swagger UI will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Integration Testing
Verify that all dependencies and routers are resolved properly using our test client:
```bash
# Set Python path and run test script
$env:PYTHONPATH="."  # Windows Powershell
python scratch/test_api.py
```
