# IndustryBrain-AI: Enterprise Python Backend

High-performance Python backend powering **IndustryBrain-AI** (Codename: *Sangrahalayamu*). Built with **FastAPI**, **PostgreSQL**, **Neo4j Knowledge Graph**, **Qdrant Vector DB**, and **AWS Bedrock** (Cohere Embed v3 + Qwen 235B LLM).

---

## 🏛️ High-Level System Architecture

```mermaid
graph TD
    classDef frontend fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff;
    classDef backend fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#fff;
    classDef rag fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#fff;
    classDef storage fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff;
    classDef bedrock fill:#451a03,stroke:#fb923c,stroke-width:2px,color:#fff;

    subgraph UserInterface ["1. Client Workspace Layer"]
        UI["React / Next.js Enterprise Web App<br/>(Chat, Ingestion Manager, Audit & Transparency)"]:::frontend
    end

    subgraph ApplicationLayer ["2. FastAPI Service Layer (/api/v1)"]
        API["API Gateway & Controllers<br/>(Auth, RBAC Clearance, Middleware & SSE Streams)"]:::backend
        Ingestion["Multi-Format Ingestion Pipeline<br/>(Dynamic Docling / Native Parsers & Chunking)"]:::backend
        Agents["Multi-Agent Reasoning Orchestrator<br/>(Root Cause Analysis, Safety & Maintenance Agents)"]:::backend
    end

    subgraph HybridRAG ["3. Hybrid RAG Engine"]
        Retrieval["3-Way Hybrid Retrieval & Rank Fusion<br/>(Intent Guard + Metadata + Vector + Graph RAG)"]:::rag
    end

    subgraph DataPersistence ["4. Persistence & Knowledge Base"]
        Postgres[(PostgreSQL RDBMS<br/>Metadata, Users & Audit Logs)]:::storage
        Qdrant[(Qdrant Vector DB<br/>1024-dim Cohere Embeddings)]:::storage
        Neo4j[(Neo4j Graph DB<br/>Equipment Topology & Schematics)]:::storage
    end

    subgraph FoundationAI ["5. AWS Bedrock AI Layer"]
        Cohere["AWS Bedrock Cohere Embed v3<br/>(1024-dim Vector Embeddings)"]:::bedrock
        LLM["AWS Bedrock Qwen 235B / Llama 3<br/>(Grounded Answer Generation)"]:::bedrock
    end

    %% Data flow connections
    UI <-->|HTTP REST / SSE Token Stream| API
    API -->|Document Ingestion| Ingestion
    API -->|User Query| Retrieval
    
    Ingestion -->|Metadata & Provenance| Postgres
    Ingestion -->|Generate Embeddings| Cohere -->|Store Vectors| Qdrant
    Ingestion -->|Extract Equipment Relations| Neo4j
    
    Retrieval -->|1. SQL Pre-Filter| Postgres
    Retrieval -->|2. Vector Search| Qdrant
    Retrieval -->|3. Cypher Traversal| Neo4j
    
    Retrieval -->|4. Context Fusion| Agents
    Agents <-->|Prompt & Response Stream| LLM
```

---

## ⚡ Key Implementation Highlights

### 1. Low-Memory 8GB RAM Strategy (`ENABLE_DOCLING`)
- Heavy layout models (IBM Docling) require 16GB+ RAM and can cause PyTorch `std::bad_alloc` crashes on 8GB laptops.
- Controlled via `ENABLE_DOCLING` in `backend/.env`:
  - **`ENABLE_DOCLING=False` (Default for 8GB RAM)**: Bypasses PyTorch models. Uses lightweight native parsers (`PyMuPDF`, `pdfplumber`, `python-docx`, `openpyxl`, `ezdxf`, `extract-msg`) running in **`< 50MB RAM`** and completing in **`< 2s`**.
  - **`ENABLE_DOCLING=True` (For High-Memory GPU/Servers)**: Enables IBM Docling visual layout models.

### 2. Exclusive Cohere Embed v3 Integration (1024-dim)
- Provider: `BedrockEmbeddingProvider` (`cohere.embed-multilingual-v3`).
- Sub-batching in chunks of **96 items** to satisfy AWS Bedrock's 128 max item limit.
- Qdrant Cloud collection (`Enterprise_Brain`) configured for **1024 vector dimensions** with keyword payload indices (`document_id`, `workspace_id`, `role_permissions`).

### 3. Dynamic Conversational Intent Routing
- Detects casual greetings (`"hi"`, `"hello"`) and responds immediately with **0 vector DB calls**.
- Technical questions dynamically trigger 3-way hybrid retrieval (PostgreSQL metadata pre-filtering $\rightarrow$ Qdrant vector search $\rightarrow$ Neo4j graph traversal $\rightarrow$ Weighted Rank Fusion).

---

## 🚀 Execution & Configuration

### 1. Environment Setup
```bash
cp .env.example .env
```
Ensure credentials for PostgreSQL, Qdrant Cloud, Neo4j Cloud, and AWS Bedrock are configured in `.env`.

### 2. Run Database Seeder
```bash
python scripts/seed_users.py
```
*Seeds default roles and accounts (Default Password for all: `password123`).*

### 3. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive OpenAPI documentation will be live at `http://localhost:8000/docs`.
