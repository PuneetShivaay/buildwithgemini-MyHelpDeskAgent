# 🏛️ MyHelpDeskAgent Architecture Documentation

This document describes the high-level system architecture, component relationships, cloud services integration, and security/protocol boundaries for **MyHelpDeskAgent**.

---

## 🔍 System Overview

**MyHelpDeskAgent** is built on Google's **Agent Development Kit (ADK v1.1.0)** using a decoupled architecture. The agent execution engine runs as a backend service (locally via `adk api_server` or remotely on **Vertex AI Agent Runtime**), while user interaction occurs through a lightweight **FastAPI proxy server** and a custom **HTML5/CSS3/JS Web UI** rendering **A2UI v0.8 surfaces**.

```
+-------------------------------------------------------------------------------+
|                               Browser / Frontend                              |
|   HTML5 / CSS3 / Vanilla JS Interface + Custom A2UI Surface Renderer          |
+-------------------------------------------------------------------------------+
                                      │
                                  HTTP / JSON
                                      ▼
+-------------------------------------------------------------------------------+
|                          FastAPI Proxy Server (frontend/main.py)              |
|   Translates HTTP /chat requests -> A2A Protocol messages                     |
+-------------------------------------------------------------------------------+
                                      │
                                 A2A Protocol
                                      ▼
+-------------------------------------------------------------------------------+
|                       Agent Backend (app/agent.py)                            |
|   Google ADK (v1.1.0) ReAct Agent Loop + A2UI Schema Manager Callback         |
+---------------+---------------------+-------------------+---------------------+
                │                     │                   │                     │
                ▼                     ▼                   ▼                     ▼
        +---------------+     +---------------+   +---------------+     +---------------+
        |  Vertex AI    |     | Google Cloud  |   | Google Cloud  |     |  Google GenAI |
        |  Memory Bank  |     |   Firestore   |   |    Storage    |     | Imagen & Omni |
        | (Preferences) |     |  (DB Schema)  |   | (Asset Host)  |     |  (Media Tools)|
        +---------------+     +---------------+   +---------------+     +---------------+
```

---

## 🧩 Core Architectural Components

### 1. Frontend Proxy Layer (`frontend/main.py` & `frontend/static/index.html`)
- **Web UI Client**: Modern single-page web interface with dark/light themes, prompt chips, typing indicators, quick action buttons, and a built-in A2UI catalog v0.8 renderer.
- **FastAPI A2A Proxy**: Decouples the browser from direct agent authentication tokens. It converts incoming HTTP POST requests (`/chat`) into Agent-to-Agent (A2A) protocol streams, forwarding them to the deployed Agent Runtime or local ADK instance.

### 2. Core Agent Engine (`app/agent.py`)
- **ADK LlmAgent**: Orchestrates model execution, tool dispatching, code execution in sandbox, and memory retrieval.
- **A2UI Schema Manager Callback** (`app/a2ui_utils.py`): Post-processes agent tool outputs and model responses, injecting structured A2UI card parts into the A2A response stream.

### 3. State & Persistence Layer
- **Google Cloud Firestore**: Persists domain data across two primary collections:
  - `tickets`: Stores IT support tickets (`TCK-xxxx`), priority, status, category, owner, and resolution notes.
  - `hardware`: Stores assigned enterprise hardware inventory (`HW-xxxx`), specs, assigned employee names, and serial numbers.
- **Vertex AI Memory Bank**: Managed vector memory service (`VertexAiMemoryBankService` in `us-east1`). Automatically retrieves long-term employee preferences across sessions via `PreloadMemoryTool` and persists new memories post-invocation via `generate_memories_callback`.

### 4. Multimodal Generation & Storage
- **Google Gen AI Models**:
  - `gemini-3.1-flash-lite-image`: Generates technical troubleshooting and setup guide diagrams.
  - `gemini-omni-flash-preview` (Region: `global`): Produces video tutorials for hardware maintenance.
- **Google Cloud Storage (GCS)**: Public bucket (`it-helpdesk-assets-...`) hosting generated image and video bytes, returning immutable public HTTPS URLs to the frontend.

---

## 🛡️ Protocol & Security Boundaries

1. **A2A (Agent-to-Agent) Protocol**: All communication between the FastAPI proxy server and the Agent Runtime follows Google's A2A 1.1.0 standard stream query specification.
2. **Service Account Identity**: When deployed to Cloud Run, the frontend service account uses Google Cloud Application Default Credentials (ADC) with `roles/aiplatform.user` to securely access the Vertex AI Agent Engine endpoint.
3. **Sandbox Code Execution**: Code evaluation for SLA metrics (`calculate`) is strictly contained within `AgentEngineSandboxCodeExecutor`, preventing unauthorized system access.
