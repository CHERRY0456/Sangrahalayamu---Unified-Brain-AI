# IndustryBrain-AI: Enterprise Knowledge Intelligence Platform

**IndustryBrain-AI** (Codename: *Sangrahalayamu*) is an enterprise Knowledge-Augmented Generation (KAG) and Multi-Agent Orchestration platform designed for industrial plant diagnostics, compliance management, and equipment failure intelligence.

---

## 🏛️ System Architecture

```mermaid
graph LR
    classDef client fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff;
    classDef app fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#fff;
    classDef rag fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#fff;
    classDef db fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff;
    classDef ai fill:#451a03,stroke:#fb923c,stroke-width:2px,color:#fff;

    subgraph UI ["1. Client UI"]
        A["Next.js Web App<br/>(Chat, Ingestion, Audit)"]:::client
    end

    subgraph API ["2. Core API & Ingestion"]
        B["FastAPI Backend<br/>(/api/v1)"]:::app
        C["Ingestion Engine<br/>(Docling Toggle / Native)"]:::app
    end

    subgraph RAG ["3. Hybrid RAG & Agents"]
        D["Hybrid Retrieval<br/>(Intent Guard + Rank Fusion)"]:::rag
        E["Multi-Agent Orchestrator<br/>(RCA, Safety, Maintenance)"]:::rag
    end

    subgraph DB ["4. Data & Knowledge Base"]
        F[(PostgreSQL<br/>Meta & RBAC)]:::db
        G[(Qdrant Vector DB<br/>1024-dim)]:::db
        H[(Neo4j Graph DB<br/>Equipment Topology)]:::db
    end

    subgraph AI ["5. AWS Bedrock Cloud"]
        I["Cohere Embed v3<br/>(1024-dim Embeddings)"]:::ai
        J["Qwen 235B LLM<br/>(AI Response Generation)"]:::ai
    end

    A <-->|REST / SSE Stream| B
    B -->|Upload Documents| C
    B -->|Chat Request| D
    
    C -->|Metadata & Logs| F
    C -->|Generate Vectors| I -->|Store Embeddings| G
    C -->|Build Topology| H

    D -->|1. SQL Pre-Filter| F
    D -->|2. Vector Search| G
    D -->|3. Graph Traversal| H
    D -->|Context Package| E
    E <-->|Prompt & Stream| J
```

---

## 🌟 Core System Pillars

### 1. 3-Way Hybrid RAG Engine
- **Vector Similarity (Qdrant Cloud)**: AWS Bedrock **Cohere Embed v3** (`cohere.embed-multilingual-v3`) with **1024-dimension** vectors.
- **Knowledge Graph (Neo4j Cloud)**: Maps plant equipment topology (e.g. `P&ID 402` $\rightarrow$ `Valve V-102` $\rightarrow$ `Pump P-1`).
- **PostgreSQL Pre-Filtering**: Applies role-based security clearances (CEO, Engineer, Technician) and metadata constraints before vector/graph rank fusion.

### 2. Multi-Format Industrial Ingestion
- Support for `.pdf`, `.docx`, `.xlsx`/`.csv`, `.pptx`, `.dxf` (AutoCAD drawings), `.msg`/`.eml`, `.log`, and images (OCR via Tesseract).

### 3. ⚡ Low-Memory 8GB RAM Optimization (`ENABLE_DOCLING`)
- **`ENABLE_DOCLING=False` (Default for 8GB RAM)**: Bypasses PyTorch models. Activates high-speed native parsers (`PyMuPDF`, `pdfplumber`, `python-docx`, `openpyxl`, `ezdxf`) running in **`< 50MB RAM`** and **`< 2s`** with 0 memory crashes.
- **`ENABLE_DOCLING=True` (For High-Memory Servers)**: Enables IBM Docling visual layout models.

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
