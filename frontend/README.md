# IndustryBrain-AI: Next.js Frontend

This is the Next.js frontend client for IndustryBrain-AI. It is built using the Next.js App Router, styled with TailwindCSS, and integrated with the FastAPI backend using Server-Sent Events (SSE) for streaming responses and multipart upload APIs.

---

## 🛠️ Key UI Features

1. **Dashboard & Metrics Panel**: A unified workspace overview displaying active ingestion statuses, system health, and proactive recommendations.
2. **Document Ingestion Studio (`/upload`)**: A multi-step ingestion helper:
   - **Step 1**: Ingest files (queue files locally).
   - **Step 2**: Add metadata (select document categories like blueprint/SOP and add descriptions).
   - **Step 3**: Review details and commit to the layout-aware AI parsing pipeline.
3. **AI Processing Studio (`/processing`)**: Visualizes the processing pipeline (OCR extraction, coordinate evaluations, entity canonicalization, graph build, and vector indexing).
4. **Diagnostic Chat & Explainability Workspace (`/chat`)**:
   - Streams reasoning answers in real-time.
   - Provides a split-screen **AI Explainability Panel** which exposes confidence ratings, document coverage, exact citation text snippets, sequential reasoning tracks, and Neo4j relationship maps.

---

## 📂 Frontend Structure

- **`app/`**: Next.js App Router endpoints (`/chat`, `/upload`, `/processing`, etc.).
- **`components/`**: Atomic, reusable interface widgets.
- **`features/`**: Modular logic directories housing component dependencies:
  - `chat/`: Chat input bubbles, sidebars, and request access overrides.
  - `upload/`: Ingestion zones, metadata forms, and progress reviews.
  - `transparency/`: Explanations, citations, confidence bars, and reasoning timelines.
  - `persona/`: RBAC restrictions and persona focus perspective overrides.
- **`services/`**: Class wrappers encapsulating API endpoints (`chat-service.ts`, `upload-service.ts`).
- **`store/`**: Global state management (Zustand context).
- **`lib/`**: Network abstraction layer (`api-client.ts`).

---

## 🚀 Setup & Development

### 1. Install Node Dependencies
Ensure you have Node.js 18+ installed, then run:
```bash
npm install
```

### 2. Configure Local Environment Variables
Create a `.env.local` file in the root of the `/frontend` directory:
```bash
# Point to your FastAPI backend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Dev Server
Launch the local web server:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.
