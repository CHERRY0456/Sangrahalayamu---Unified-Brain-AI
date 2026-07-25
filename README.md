# IndustryBrain-AI: Enterprise Knowledge Intelligence Platform

**IndustryBrain-AI** (Codename: *Sangrahalayamu*) is an enterprise-grade Knowledge-Augmented Generation (KAG) and Multi-Agent Orchestration platform designed for industrial plant diagnostics, compliance management, and equipment failure intelligence. It bridges heterogeneous unstructured manuals, P&ID schematics, spreadsheets, CAD drawings, email archives, and operational logs with a 3-Way Hybrid Retrieval Engine (Qdrant Vector DB + Neo4j Graph DB + PostgreSQL Metadata RDBMS) and AWS Bedrock (Cohere Embed v3 + Qwen 235B LLM).

---

## 🏗️ Detailed System Architecture

```mermaid
flowchart TB
    subgraph ClientLayer ["1. Presentation Layer (Next.js 14 App Router)"]
        UI["React Workspace UI<br/>(/chat, /upload, /audit, /dashboard)"]
        SSEClient["SSE Stream Reader"]
        TransparencyUI["Transparency & Explainability Panel<br/>(Citations, Reasoning Graph, Confidence Metrics)"]
        APIClient["API Client (Bearer JWT Token Injector)"]
    end

    subgraph APILayer ["2. API & Security Layer (FastAPI /api/v1)"]
        Middleware["Middleware Stack<br/>(CORS, Correlation ID, Response Timing)"]
        AuthRouter["/api/v1/auth<br/>(JWT Login, Refresh, Session)"]
        UploadRouter["/api/v1/upload<br/>(Ingestion Manager)"]
        ChatRouter["/api/v1/chat<br/>(SSE Streaming & Q&A)"]
        AuditRouter["/api/v1/audit<br/>(Compliance Activity Logs)"]
        AccessRouter["/api/v1/access<br/>(RBAC Clearance Overrides)"]
    end

    subgraph IngestionPipeline ["3. Multi-Format Ingestion Pipeline"]
        Detector["Format & Magic Byte Detector"]
        
        subgraph Parsers ["Modality-Aware Parsers Suite"]
            DoclingP["DoclingParser<br/>(Toggle: ENABLE_DOCLING)"]
            PdfP["PyPDF / PyMuPDF Parser"]
            OfficeP["Office Parser (DOCX, PPTX)"]
            SheetP["Spreadsheet Parser (XLSX, CSV)"]
            CadP["AutoCAD DXF Parser (ezdxf)"]
            EmailP["Email Archive Parser (EML, MSG)"]
            LogP["Log & Runbook Parser"]
            OcrP["OCR Router (Tesseract)"]
        end
        
        Chunking["Layout-Aware Chunking Stage"]
        EntityStage["Entity & Relation Extraction Stage"]
        VectorIndexer["Cohere Vector Indexer (1024-dim)"]
    end

    subgraph RetrievalEngine ["4. 3-Way Hybrid RAG Engine (Retrieval Orchestrator)"]
        IntentRouter{"Intent Routing Guard<br/>(Casual Greeting?)"}
        SqlFilter["Step 1: PostgreSQL Candidate Metadata Pre-Filtering"]
        VectorSearch["Step 2: Qdrant Semantic Vector Search"]
        GraphSearch["Step 3: Neo4j Cypher Graph Traversal"]
        RbacGuard["Step 4: Policy Engine Security Clearance Guard"]
        RankFusion["Step 5: Weighted Rank Fusion<br/>(0.60 Semantic / 0.25 Graph / 0.15 Metadata)"]
    end

    subgraph AgentOrchestration ["5. AI Reasoning & Multi-Agent Framework"]
        AgentOrch["Agent Orchestrator"]
        RcaAgent["Root Cause Analysis (RCA) Agent"]
        SafetyAgent["Compliance & Safety Agent"]
        MaintenanceAgent["Proactive Maintenance Agent"]
        PromptEng["Prompt Engine (PromptBuilder)"]
        Validator["Response Validator & Formatter"]
    end

    subgraph PersistenceLayer ["6. Persistence & Foundation Models"]
        PostgresDB[(PostgreSQL RDBMS<br/>Users, Document Meta, Audit Logs)]
        QdrantDB[(Qdrant Cloud Vector DB<br/>1024-dim Collection: Enterprise_Brain)]
        Neo4jDB[(Neo4j Cloud Graph DB<br/>Equipment Topology & Relations)]
        BedrockEmbed["AWS Bedrock Cohere Embed v3<br/>(cohere.embed-multilingual-v3)"]
        BedrockLLM["AWS Bedrock Qwen 235B LLM<br/>(qwen.qwen3-vl-235b-a22b)"]
    end

    %% Client to API
    UI --> APIClient
    APIClient --> Middleware
    Middleware --> AuthRouter & UploadRouter & ChatRouter & AuditRouter & AccessRouter

    %% Upload Flow
    UploadRouter --> Detector
    Detector --> Parsers
    Parsers --> Chunking --> EntityStage --> VectorIndexer
    VectorIndexer -->|Store Chunks & Embeddings| QdrantDB
    EntityStage -->|Store Equipment Nodes| Neo4jDB
    VectorIndexer -->|Store Document Records| PostgresDB
    VectorIndexer -->|Generate 1024-dim Vectors| BedrockEmbed

    %% Chat Flow
    ChatRouter --> IntentRouter
    IntentRouter -->|Casual Greeting| PromptEng
    IntentRouter -->|Technical Domain Query| SqlFilter
    
    SqlFilter -->|Query Candidates| PostgresDB
    SqlFilter --> VectorSearch & GraphSearch
    VectorSearch -->|1024-dim Search| QdrantDB
    GraphSearch -->|Cypher Traversal| Neo4jDB
    
    VectorSearch & GraphSearch --> RbacGuard
    RbacGuard -->|Check Clearance| PostgresDB
    RbacGuard --> RankFusion --> AgentOrch
    
    AgentOrch --> RcaAgent & SafetyAgent & MaintenanceAgent
    AgentOrch --> PromptEng
    PromptEng --> BedrockLLM
    BedrockLLM --> Validator
    Validator -->|Yield SSE Event Stream| ChatRouter
    ChatRouter -->|Stream Tokens & Metadata| SSEClient
    SSEClient --> UI & TransparencyUI
```

---

## 🌟 Core Architecture Modules

### 1. Presentation Layer (Next.js 14 App Router)
- **Interactive Workspaces**: AI Chat (`/chat`), Ingestion Manager (`/upload`), Compliance Audit (`/audit`), and Metric Dashboards (`/`).
- **Transparency & Explainability**: Real-time rendering of reasoning steps, document citations, overall confidence metrics, and interactive Neo4j node relationship graphs.
- **Bearer JWT Injection**: Standardized client fetching automatically attaching authentication headers.

### 2. Decoupled API Layer (FastAPI `/api/v1`)
- **Middleware Chain**: Outermost CORS resolution, correlation ID context tracking, and response execution timing headers.
- **API Endpoints**: `/api/v1/auth`, `/api/v1/upload`, `/api/v1/chat`, `/api/v1/audit`, `/api/v1/access`, `/api/v1/dashboard`.

### 3. Multi-Format Industrial Ingestion Pipeline
- **Modality-Aware Inspection**: Auto-detects MIME types and magic byte headers for `.pdf`, `.docx`, `.xlsx`, `.csv`, `.pptx`, `.dxf` (AutoCAD drawings), `.msg`/`.eml`, `.log`, and images.
- **⚡ Low-Memory 8GB RAM Strategy (`ENABLE_DOCLING`)**:
  - `ENABLE_DOCLING=False` *(Default for 8GB RAM)*: Bypasses heavy PyTorch models. Activates high-speed native parsers (`PyMuPDF`, `pdfplumber`, `python-docx`, `openpyxl`, `ezdxf`) running in **`< 50MB RAM`** and completing in **`< 2s`**.
  - `ENABLE_DOCLING=True` *(For High-Memory GPU/Servers)*: Enables IBM Docling visual layout models.

### 4. 3-Way Hybrid RAG Retrieval Engine
- **Intent Routing Guard**: Bypasses vector DB search for general greetings (`"hi"`, `"hello"`).
- **PostgreSQL Candidate Pre-filtering**: Filters document candidate IDs using metadata tags.
- **Qdrant Vector Similarity**: Executes semantic vector search using **1024-dimension Cohere Embed v3** vectors.
- **Neo4j Graph Traversal**: Queries equipment topological node relationships (e.g. `P&ID 402` $\rightarrow$ `Valve V-102` $\rightarrow$ `Pump P-1`).
- **PolicyEngine RBAC Guard**: Filters candidates against user security clearance roles (CEO, Engineer, Technician).
- **Weighted Rank Fusion**: Merges scores using normalized weights (0.60 Semantic / 0.25 Graph / 0.15 Metadata).

### 5. Multi-Agent Reasoning & Foundation Layer
- **Autonomous Agents**: Root Cause Analysis (RCA), Compliance Verification, and Maintenance Recommendation agents.
- **AWS Bedrock Integration**: Cohere Embed v3 (`cohere.embed-multilingual-v3`) + Qwen 235B LLM (`qwen.qwen3-vl-235b-a22b`).

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
