# Contributing to MyHelpDeskAgent

Thank you for your interest in contributing to **MyHelpDeskAgent**! This document provides guidelines and standards for building, testing, and submitting contributions to ensure enterprise-grade code quality.

---

## 📜 Code of Conduct

We expect all contributors to adhere to a respectful and inclusive environment:
- Be respectful of differing opinions and technical feedback.
- Focus on what is best for the project community and user experience.
- Gracefully accept constructive criticism.

---

## 🛠️ Development Workflow

### 1. Fork and Clone
```bash
git clone https://github.com/PuneetShivaay/buildwithgemini-MyHelpDeskAgent.git
cd buildwithgemini-MyHelpDeskAgent
```

### 2. Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Creating a Feature Branch
Use descriptive branch naming conventions:
- `feature/add-jira-integration`
- `fix/a2ui-rendering-bug`
- `docs/update-architecture-diagram`

```bash
git checkout -b feature/your-feature-name
```

---

## 🧪 Code Quality & Testing Standards

Before committing your changes, ensure code quality checks pass:

### Linting & Formatting
We follow standard Python PEP 8 conventions enforced by `ruff`:
```bash
ruff check app/ frontend/
ruff format --check app/ frontend/
```

### Type Checking
Ensure all function signatures and public APIs include proper Python type annotations:
```bash
mypy app/ frontend/
```

---

## 📥 Submitting Pull Requests (PRs)

When opening a Pull Request:
1. **Title**: Use clear, conventional commit titles (e.g., `feat(tools): add network ping diagnostic tool`).
2. **Description**: Describe **what** was changed, **why** it was changed, and **how** to verify it.
3. **Documentation**: Update relevant markdown files under `doc/` and `README.md` if function signatures or environment variables changed.
4. **Verification**: Include manual test notes or automated test logs confirming no regressions.

---

## 🔒 Security Vulnerabilities

Do **NOT** report security vulnerabilities via public GitHub issues. Please refer to our [SECURITY.md](SECURITY.md) guidelines for private disclosure procedures.
