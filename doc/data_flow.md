# 🔄 MyHelpDeskAgent Data Flow Documentation

This document describes the end-to-end data flow sequences for user interactions, tool execution, and A2UI surface rendering in **MyHelpDeskAgent**.

---

## 🔁 1. General User Interaction Flow

```
[User Types Prompt in Web UI]
         │
         ▼
[Frontend JavaScript (sendPrompt)]
   POST /chat JSON Payload: {"message": "Check assigned hardware for Alice Smith"}
         │
         ▼
[FastAPI Proxy (frontend/main.py)]
   Translates payload -> A2A Protocol Stream
   Routes to Agent Runtime Endpoint
         │
         ▼
[Agent Engine (app/agent.py)]
   1. PreloadMemoryTool fetches long-term user memories
   2. LLM evaluates intent and triggers get_hardware_info(identifier="Alice Smith")
         │
         ▼
[Firestore Database]
   Queries `hardware` collection where assigned_to == "Alice Smith"
   Returns: {asset_id: "HW-8801", device_name: "MacBook Pro 16\" M3 Max", ...}
         │
         ▼
[A2UI Callback (app/a2ui_utils.py)]
   Transforms Firestore result into structured A2UI v0.8 Card JSON:
   Card > Column > [Title, Asset ID, Device Name, Status/SN]
         │
         ▼
[A2A Protocol Stream Response]
   Pushes A2UI JSON payload back to FastAPI Proxy
         │
         ▼
[Browser DOM Renderer]
   Parses A2UI JSON and renders styled UI card surface in chat container
```

---

## 🎨 2. Multimodal Generation Data Flow (Image / Video)

```
[User Prompt: "Generate a setup diagram for dual monitors"]
         │
         ▼
[LLM Tool Selection: generate_setup_guide_image]
         │
         ▼
[Google GenAI Client (Vertex AI)]
   Calls `gemini-3.1-flash-lite-image` with prompt
   Receives raw PNG/JPG image bytes
         │
         ├──────────────────────────────────────────────┐
         ▼                                              ▼
[ADK ToolContext.save_artifact]             [Google Cloud Storage Client]
   Saves artifact for Playground               Uploads bytes to public GCS bucket
                                               Returns: https://storage.googleapis.com/...
                                                        │
                                                        ▼
                                            [A2UI Schema Manager]
                                               Builds Card > Column > [Title, Image, Caption]
                                                        │
                                                        ▼
                                            [Web UI Displays Diagram]
```

---

## 🧠 3. Memory Extraction Flow

```
[Agent Completes Interaction Turn]
         │
         ▼
[generate_memories_callback Execution]
   Parses user conversation history for preferences (e.g. OS choice, workstation location)
         │
         ▼
[Vertex Ai Memory Bank Service]
   Stores extracted memory vector in us-east1 Memory Bank instance
         │
         ▼
[Available for Next Session Retrieval via PreloadMemoryTool]
```
