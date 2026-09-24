# Production Deployment Guide

This document details the step-by-step production deployment workflow for **MyHelpDeskAgent** on **Google Cloud Platform (GCP)**, covering Vertex AI Agent Runtime deployment, Cloud Run proxy setup, IAM permissions, and secret management.

---

## 🏗️ Architecture Overview & Target Services

```
[ User Browser ]
       │
       ▼ (HTTPS / Public Traffic)
[ Google Cloud Run (Frontend Proxy) ]
       │
       ▼ (A2A Protocol over Google API Gateway)
[ Vertex AI Agent Runtime (Reasoning Engine) ]
       │
       ├──► [ Google Cloud Firestore ] (Tickets & Hardware DB)
       ├──► [ Vertex AI Memory Bank ] (Long-Term User Memory)
       └──► [ Google Cloud Storage ] (Public Multimodal Media Assets)
```

---

## 📋 Prerequisites & IAM Setup

### Required GCP APIs
Enable all required GCP service APIs:
```bash
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### Required Service Account IAM Roles
Assign minimal required IAM roles to the Compute Service Account (e.g. `<PROJECT_NUMBER>-compute@developer.gserviceaccount.com`):

```bash
PROJECT_ID="<YOUR_GCP_PROJECT_ID>"
SERVICE_ACCOUNT="<PROJECT_NUMBER>-compute@developer.gserviceaccount.com"

# 1. Vertex AI Reasoning Engine execution
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

# 2. Firestore read/write access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

# 3. Cloud Storage media management
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"
```

---

## 🚀 Step 1: Deploy Agent Backend to Vertex AI Agent Runtime

Deploy the Python agent defined in `app/agent.py` using `agents-cli`:

```bash
# 1. Set active project
gcloud config set project <YOUR_GCP_PROJECT_ID>

# 2. Deploy agent runtime
agents-cli deploy
```

Upon successful deployment, `agents-cli` outputs your Reasoning Engine Resource ID:
```
Resource Name: projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<ENGINE_ID>
```

---

## 🚀 Step 2: Deploy Frontend Proxy to Google Cloud Run

Deploy the FastAPI proxy container (`frontend/`) to Google Cloud Run in `us-east1`:

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

---

## 🔍 Verification & Health Checks

Once deployed:

1. **Query Cloud Run Service URL**:
   ```bash
   gcloud run services describe frontend --region us-east1 --format="value(status.url)"
   ```

2. **Test HTTP Health Status**:
   ```bash
   curl -i https://<SERVICE_NAME>-<HASH>-ue.a.run.app
   ```

3. **Verify A2A Agent Card Fetch**:
   ```bash
   curl -i https://us-east1-aiplatform.googleapis.com/reasoningEngines/v1/projects/<PROJECT_NUMBER>/locations/us-east1/reasoningEngines/<ENGINE_ID>/api/a2a/app/.well-known/agent-card.json
   ```

---

## 🛡️ Operations, Logs & Troubleshooting

- **Cloud Run Logs**:
  ```bash
  gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="frontend"' --limit=50
  ```

- **Vertex AI Agent Logs**:
  ```bash
  gcloud logging read 'resource.type="aiplatform.googleapis.com/ReasoningEngine"' --limit=50
  ```
