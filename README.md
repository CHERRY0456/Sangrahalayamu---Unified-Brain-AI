# IndustryBrain-AI: Enterprise Knowledge Intelligence Platform

**IndustryBrain-AI** (Codename: *Sangrahalayamu*) is an enterprise-grade Knowledge-Augmented Generation (KAG) and Multi-Agent Orchestration platform designed for industrial plant diagnostics, compliance management, and equipment failure intelligence. It bridges heterogeneous unstructured manuals, P&ID schematics, spreadsheets, CAD drawings, email archives, and operational logs with a 3-Way Hybrid Retrieval Engine (Qdrant Vector DB + Neo4j Graph DB + PostgreSQL Metadata RDBMS) and AWS Bedrock (Cohere Embed v3 + Qwen 235B LLM).

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

## 🌟 Core System Pillars

### 1. 3-Way Hybrid RAG Engine
- **Vector Similarity (Qdrant Cloud)**: Driven exclusively by AWS Bedrock **Cohere Embed v3** (`cohere.embed-multilingual-v3`) configured for **1024-dimension** vectors.
- **Knowledge Graph (Neo4j Cloud)**: Maps plant equipment topology (e.g. `P&ID 402` $\rightarrow$ `Valve V-102` $\rightarrow$ `Pump P-1`).
- **PostgreSQL Pre-Filtering**: Applies role-based security clearances (CEO, Engineer, Technician) and metadata constraints before vector/graph rank fusion.

### 2. Multi-Format Industrial Ingestion
- Native support for `.pdf` (manuals/P&IDs), `.docx`, `.xlsx`/`.csv` (spreadsheets), `.pptx`, `.dxf` (AutoCAD schematics), `.msg`/`.eml` (email archives), `.log` (system traces), and scanned images (Tesseract OCR).

### 3. ⚡ Low-Memory 8GB RAM Optimization (`ENABLE_DOCLING`)
- **`ENABLE_DOCLING=False` (Default for 8GB RAM)**: Bypasses heavy PyTorch models. Activates high-speed native parsers (`PyMuPDF`, `pdfplumber`, `python-docx`, `openpyxl`, `ezdxf`) running in **`< 50MB RAM`** and **`< 2s`** with 0 memory crashes.
- **`ENABLE_DOCLING=True` (For High-Memory Servers)**: Enables IBM Docling visual layout models.

### 4. Dynamic Intent Routing & Transparency
- Bypasses vector DB searches for general greetings (`"hi"`, `"hello"`).
- Injects full document citations, confidence metrics, reasoning steps, and interactive node graphs for technical queries.

---

## ⚡ Quick Start Guide

### 1. Backend Execution
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Mac/Linux

pip install -r requirements.txt
cp .env.example .env

# Seed test database users
python scripts/seed_users.py

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Execution
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 🔑 Seed Test Credentials

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **CEO** | `cherry@company.com` | `password123` | Full Enterprise Clearance |
| **Maintenance Engineer** | `priya.sharma@company.com` | `password123` | Engineering & Maintenance |
| **Field Technician** | `ravi.kumar@company.com` | `password123` | Operational Logs & Manuals |
| **Compliance Manager** | `neha.iyer@company.com` | `password123` | Audit & Regulatory Compliance |
