# 🎨 MyHelpDeskAgent Design Patterns Documentation

This document highlights the key software engineering and AI design patterns implemented throughout **MyHelpDeskAgent**.

---

## 1. ReAct (Reasoning + Acting) Agent Pattern
- **Implementation**: Managed by Google ADK's `LlmAgent`.
- **Purpose**: The agent continuously cycles through **Thought -> Action (Tool Call) -> Observation (Tool Result) -> Final Response**.
- **Example Flow**:
  1. User asks: *"Check support ticket TCK-1002"*
  2. **Thought**: I need to query Firestore for ticket `TCK-1002`.
  3. **Action**: Invokes `get_ticket_status(ticket_id="TCK-1002")`.
  4. **Observation**: Returns ticket dictionary `{status: 'In Progress', priority: 'High', ...}`.
  5. **Final Response**: Formats response as an A2UI status card.

---

## 2. Proxy / Gateway Pattern
- **Implementation**: `frontend/main.py` (FastAPI).
- **Purpose**: Acts as a reverse proxy between the client browser and the Vertex AI Agent Engine endpoint.
- **Benefits**:
  - Encapsulates authentication credentials (ADC / Google OAuth tokens).
  - Normalizes raw A2A protocol streams into simple JSON payloads for web clients.
  - Prevents exposing direct internal GCP resource endpoints to client-side code.

---

## 3. Callback / Interceptor Pattern
- **Implementation**: `a2ui_callback` in `app/a2ui_utils.py` and `generate_memories_callback` in `app/agent.py`.
- **Purpose**: Intercepts model generation lifecycle events without modifying core model logic.
  - **A2UI Callback**: Intercepts raw tool outputs and injects formatted A2UI catalog UI JSON into the response payload.
  - **Memory Callback**: Executes post-generation, evaluating whether new user preferences (e.g. preferred OS, workstation setup) should be saved to Vertex AI Memory Bank.

---

## 4. Factory & Schema Manager Pattern
- **Implementation**: `A2uiSchemaManager` in `app/a2ui_utils.py`.
- **Purpose**: Provides a centralized builder for constructing standard A2UI v0.8 components (`Card`, `Column`, `Row`, `Text`, `Image`).
- **Benefits**:
  - Guarantees valid component structure according to A2UI v0.8 catalog definitions.
  - Eliminates hardcoded JSON template duplication across tool functions.

---

## 5. Dual Artifact & Storage Pattern
- **Implementation**: Used in `generate_setup_guide_image` and `generate_hardware_video`.
- **Purpose**: Solves dual-environment requirements for generated media:
  1. **Playground Compatibility**: Saves raw bytes as an ADK artifact via `tool_context.save_artifact()` for local ADK Playground rendering.
  2. **Production Hosting**: Streams raw bytes directly to a public Google Cloud Storage bucket (`it-helpdesk-assets-...`), returning a durable public HTTPS URL for web clients.

---

## 6. Pre-Execution Dependency Injection
- **Implementation**: `PreloadMemoryTool` in `app/agent.py`.
- **Purpose**: Preloads historical facts and employee state into model prompt context before execution starts, enabling seamless personalization without manual user context injection.
