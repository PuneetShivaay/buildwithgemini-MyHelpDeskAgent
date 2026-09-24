# 🤖 MyHelpDeskAgent

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Google ADK 1.1.0](https://img.shields.io/badge/Google%20ADK-1.1.0-4285F4.svg)](https://google.github.io/agent-development-kit/)
[![Cloud Run Deployed](https://img.shields.io/badge/Google%20Cloud%20Run-Deployed-34A853.svg)](https://frontend-246073422784.us-east1.run.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI Pipeline](https://github.com/PuneetShivaay/buildwithgemini-MyHelpDeskAgent/actions/workflows/ci.yml/badge.svg)](https://github.com/PuneetShivaay/buildwithgemini-MyHelpDeskAgent/actions)

> 🌐 **Live Production Web Application**: [https://frontend-246073422784.us-east1.run.app](https://frontend-246073422784.us-east1.run.app)

**MyHelpDeskAgent** is an enterprise-grade AI IT Helpdesk & Support assistant built with Google's **Agent Development Kit (ADK v1.1.0)**. It automates IT support ticketing, hardware inventory lookups, network diagnostics, multimodal setup guide generation (diagrams & videos), and SLA calculation metrics—all presented through rich **A2UI card surfaces** and backed by cross-session **Vertex AI Memory Bank**.

![MyHelpDeskAgent Interactive Demo Walkthrough](demo/demo_walkthrough.gif)

---

## 📌 Table of Contents
- [✨ Key Architecture & Features](#-key-architecture--features)
- [📚 Technical Documentation Suite](#-technical-documentation-suite)
- [📁 Repository Structure](#-repository-structure)
- [💻 Step-by-Step Local Setup & Execution](#-step-by-step-local-setup--execution)
- [🚀 Cloud Deployment Guide](#-cloud-deployment-guide)
- [🔐 Security & IAM Policies](#-security--iam-policies)
- [🤝 Contributing & License](#-contributing--license)

---

## ✨ Key Architecture & Features

All features listed below are directly implemented, containerized, and verified in production (`app/agent.py`, `app/a2ui_utils.py`, `frontend/main.py`, `agents-cli-manifest.yaml`).

| Feature | Tech Component | Functional Capability |
| :--- | :--- | :--- |
| 🧠 **Cross-Session Memory** | `VertexAiMemoryBankService` | Automatically extracts, retrieves, and persists user preferences, hardware specs, and support notes across separate chat sessions (`us-east1`). |
| 📊 **Firestore Inventory & Tickets** | `google-cloud-firestore` | Real-time CRUD queries on Firestore `hardware` (laptops, serials, RAM/CPU) and `tickets` (priority, status, ticket ID `TCK-xxxx`). |
| 🖼️ **Multimodal Generation** | Google GenAI & Omni Model | Generates technical setup diagrams (`gemini-3.1-flash-lite-image`) and hardware video guides (`gemini-omni-flash-preview` in `global`). |
| ☁️ **GCS Public Asset Storage** | `google-cloud-storage` | Automated media byte uploads to public Google Cloud Storage returning public HTTPS object URLs (`https://storage.googleapis.com/...`). |
| 🎨 **Native A2UI Card Surfaces** | `a2ui_callback` & Client Parser | Intercepts agent tool responses and formats them into rich interactive A2UI cards (tables, status badges, device specs). |
| ⚡ **Sandbox SLA & Diagnostics** | `AgentEngineSandboxCodeExecutor` | Executes Python sandbox math for IP subnetting and automated SLA resolution time metrics. |

---

## 📚 Technical Documentation Suite

Our repository includes a dedicated [`doc/`](doc/) engineering suite designed for developers, solution architects, and security reviewers:

| Document | Focus & Target Audience | Description |
| :--- | :--- | :--- |
| 🏗️ **[Architecture Guide](doc/architecture.md)** | Architects & DevOps | System topology, GCP service interactions, A2A protocol flow, and security perimeters. |
| 🎨 **[Design Patterns](doc/design_patterns.md)** | Senior Software Engineers | ReAct reasoning loop, Proxy/Gateway pattern, Interceptor callbacks, and Dual Storage. |
| 📂 **[Code Structure & DB Schemas](doc/code_structure.md)** | Developers | Codebase layout, complete tool reference matrix, and Firestore collection data models. |
| 🔄 **[Data Flow Sequences](doc/data_flow.md)** | Solution Engineers | End-to-end user interaction sequence diagrams, multimodal pipelines, and Memory Bank flow. |
| 🚀 **[Production Deployment Guide](doc/deployment_guide.md)** | Cloud Engineers | Step-by-step Vertex AI Reasoning Engine & Cloud Run proxy deployment guide with IAM roles. |

---

## 📁 Repository Structure

```
buildwithgemini-MyHelpDeskAgent/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI workflow (lint & syntax compile)
├── app/
│   ├── agent.py               # ADK agent, tools, Firestore DB, and Memory Bank wiring
│   ├── a2ui_utils.py          # A2UI response formatting interceptor callback
│   └── fast_api_app.py        # ADK FastAPI backend application
├── frontend/
│   ├── main.py                # FastAPI proxy server (A2A protocol bridge)
│   ├── Dockerfile             # Production container definition for Cloud Run
│   └── static/
│       └── index.html         # Multi-tab web UI (Home Overview, Live Agent Chat, Docs)
├── doc/                       # Enterprise Technical & Architecture Guides
│   ├── architecture.md        # System architecture & GCP integration
│   ├── design_patterns.md     # Software & AI agent design patterns
│   ├── code_structure.md      # Directory layout, tools & DB schemas
│   ├── data_flow.md           # Sequence diagrams & end-to-end data flows
│   └── deployment_guide.md    # Production GCP deployment & IAM role guide
├── demo/                      # Demonstration Media Assets & Walkthrough GIF
│   ├── demo_walkthrough.gif   # Looping interactive demo walkthrough
│   └── *.png                  # High-resolution UI screenshots
├── agents-cli-manifest.yaml  # Agent Runtime deployment manifest (A2A mode)
├── requirements.txt           # Unified project dependency file
├── CONTRIBUTING.md            # Open-source contribution guidelines & standards
├── SECURITY.md                # Security policy & vulnerability disclosure procedures
├── CHANGELOG.md               # Version 1.1.0 release notes
└── LICENSE                    # Official MIT License
```

---

## 💻 Step-by-Step Local Setup & Execution

Follow these step-by-step instructions to run **MyHelpDeskAgent** locally on your workstation.

### 📋 Prerequisites
- **Python**: Version `3.11` (or `3.12`)
- **Google Cloud SDK (`gcloud`)**: Installed and authenticated
- **Git**: Installed

---

### 1️⃣ Step 1: Clone the Repository
```bash
git clone https://github.com/PuneetShivaay/buildwithgemini-MyHelpDeskAgent.git
cd buildwithgemini-MyHelpDeskAgent
```

---

### 2️⃣ Step 2: Authenticate with Google Cloud
Ensure Application Default Credentials (ADC) are configured so the agent can access Vertex AI Memory Bank, Firestore, and GCS:

```bash
# Login to Google Cloud CLI
gcloud auth login

# Configure Application Default Credentials
gcloud auth application-default login

# Set your active GCP project ID
gcloud config set project <YOUR_GCP_PROJECT_ID>
```

---

### 3️⃣ Step 3: Create & Activate Virtual Environment
```bash
# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Upgrade pip & install project dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4️⃣ Step 4: Launch ADK Local Web Playground
Start the ADK Developer Web server to test tools, Memory Bank, and A2UI card outputs locally:

```bash
adk web --port 18080 .
```
Open **`http://localhost:18080`** in your browser to interact directly with the agent tools in the ADK Developer UI.

---

### 5️⃣ Step 5: Launch Full Web Application & Landing Page
In a **second terminal window**, activate your virtual environment and start the FastAPI proxy:

```bash
cd frontend

# Set environment variables
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
export PORT=8080

# Run Uvicorn server
python main.py
```

Open **`http://localhost:8080`** in your browser to experience the **Home Overview Landing Page**, **Live Chat Assistant**, and **Documentation Suite**!

---

## 🚀 Cloud Deployment Guide

To deploy the agent backend to **Vertex AI Agent Runtime**:
```bash
gcloud config set project <YOUR_GCP_PROJECT_ID>
agents-cli deploy
```

To deploy the frontend web application to **Google Cloud Run**:
```bash
cd frontend
gcloud run deploy frontend \
  --source . \
  --region us-east1 \
  --project <YOUR_GCP_PROJECT_ID> \
  --allow-unauthenticated \
  --clear-base-image \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<ENGINE_ID>",AGENT_DIRECTORY="app"
```

For complete IAM role setups, Cloud Run configurations, and environment variable references, refer to the [Production Deployment Guide](doc/deployment_guide.md).

---

## 🔐 Security & IAM Policies

Please review our [SECURITY.md](SECURITY.md) for vulnerability reporting procedures and IAM role restrictions.
- Never commit private GCP service account keys or environment credentials to version control.
- Enforce least-privilege IAM roles (`roles/aiplatform.user`, `roles/datastore.user`, `roles/storage.objectViewer`).

---

## 🤝 Contributing & License

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, type checking requirements, and pull request procedures.

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
