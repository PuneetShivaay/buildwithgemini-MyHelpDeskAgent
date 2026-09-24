# 📂 MyHelpDeskAgent Code Structure Documentation

This document provides a detailed breakdown of the codebase layout, module responsibilities, database schemas, and tool definitions for **MyHelpDeskAgent**.

---

## 📁 Directory & File Layout

```
it-helpdesk-agent/
├── app/                        # Main ADK Agent Package
│   ├── agent.py                # Agent definition, tool functions, Firestore & Memory Bank setup
│   ├── a2ui_utils.py           # A2UI catalog schema manager and formatting callback
│   └── fast_api_app.py         # ADK backend FastAPI app setup
├── frontend/                   # Web Frontend Proxy Service
│   ├── main.py                 # FastAPI proxy server (A2A protocol translation)
│   └── static/
│       └── index.html          # Chat web interface with dark/light themes & A2UI renderer
├── doc/                        # Technical & Architecture Documentation
│   ├── architecture.md         # High-level architecture & GCP integration
│   ├── design_patterns.md      # Implemented software design patterns
│   ├── code_structure.md       # File structure, tools & DB schema reference
│   └── data_flow.md            # End-to-end user & data flow sequences
├── agents-cli-manifest.yaml    # ADK deployment manifest (A2A protocol, region, app directory)
├── pyproject.toml              # Dependencies & python build configuration
└── README.md                   # Project overview & local run guide
```

---

## 🛠️ Tool Definitions Reference (`app/agent.py`)

| Tool Function | Parameters | Description |
| :--- | :--- | :--- |
| `get_ticket_status` | `ticket_id: str` | Fetches ticket details and status from Firestore `tickets` collection. |
| `create_ticket` | `category: str`, `description: str`, `priority: str`, `employee_name: str` | Creates a new IT support ticket (`TCK-xxxx`) in Firestore. |
| `update_ticket_status` | `ticket_id: str`, `new_status: str`, `resolution_notes: str` | Updates ticket status and appends resolution notes in Firestore. |
| `list_user_tickets` | `employee_name: str` | Retrieves all support tickets submitted by a given employee. |
| `get_hardware_info` | `identifier: str` | Searches Firestore `hardware` collection by Asset ID (`HW-xxxx`) or assigned employee name. |
| `lookup_ip_address` | `ip_address: str` | Performs IP geolocation, ISP, and network organization diagnostics via `ip-api.com`. |
| `generate_setup_guide_image`| `topic: str`, `tool_context: ToolContext` | Generates a setup diagram using Google GenAI image model, saves artifact, and uploads to GCS. |
| `generate_hardware_video` | `topic: str`, `tool_context: ToolContext` | Generates a video tutorial using Google Omni model (`gemini-omni-flash-preview`), saves artifact, and uploads to GCS. |
| `calculate` | `expression: str` | Safely evaluates math & SLA metrics in `AgentEngineSandboxCodeExecutor`. |

---

## 🗄️ Firestore Database Schema

### 1. `tickets` Collection
```json
{
  "ticket_id": "TCK-1001",
  "category": "Hardware",
  "description": "Laptop screen flickers on HDMI connection",
  "priority": "High",
  "employee_name": "Alice Smith",
  "status": "In Progress",
  "created_at": "2026-09-24T10:00:00Z",
  "resolution_notes": "Replacement cable dispatched"
}
```

### 2. `hardware` Collection
```json
{
  "asset_id": "HW-8801",
  "device_name": "MacBook Pro 16\" M3 Max",
  "serial_number": "SN-C02XL9981",
  "assigned_to": "Alice Smith",
  "status": "Assigned",
  "purchase_date": "2024-01-15"
}
```
