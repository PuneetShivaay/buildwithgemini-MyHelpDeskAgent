# Changelog

All notable changes to **MyHelpDeskAgent** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-09-24

### 🚀 Added
- **Core Agent Rebranding**: Rebranded agent to `MyHelpDeskAgent` across codebase, manifest, and deployment configurations.
- **Vertex AI Memory Bank Service Integration**: Added `VertexAiMemoryBankService` for cross-session long-term memory extraction and preloading.
- **Firestore Database Storage**: Implemented live Firestore CRUD integration for `hardware` inventory and `tickets` management collections.
- **Multimodal Generation Tools**: Added network diagram generation via `gemini-3.1-flash-lite-image` and short hardware tutorial video generation via `gemini-omni-flash-preview` in `global` region.
- **GCS Media Upload**: Automated media byte upload to public Google Cloud Storage bucket returning public HTTPS object URLs.
- **Python Sandbox Execution**: Integrated `AgentEngineSandboxCodeExecutor` for SLA metric calculations and IP subnetting math.
- **FastAPI Proxy Server & A2A Bridge**: Built lightweight proxy (`frontend/main.py`) translating browser requests into A2A protocol messages for Agent Runtime.
- **Production Web UI & Landing Page**: Created multi-tab web application (`frontend/static/index.html`) featuring:
  - 🏠 **Home Overview Landing Page** with gradient hero, capability matrix, and system architecture pipeline.
  - 💬 **Live Chat Assistant** with interactive A2UI card surface rendering.
  - 📚 **Technical Documentation Matrix** linking to system guides.
- **Technical Documentation Suite**: Created comprehensive markdown documentation in `doc/`:
  - `doc/architecture.md`
  - `doc/design_patterns.md`
  - `doc/code_structure.md`
  - `doc/data_flow.md`
  - `doc/deployment_guide.md`
- **CI/CD Automation**: Added GitHub Actions workflow (`.github/workflows/ci.yml`) for automated linting and syntax validation.
