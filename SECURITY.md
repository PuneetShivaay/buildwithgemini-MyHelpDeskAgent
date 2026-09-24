# Security Policy & Guidelines

## 🛡️ Supported Versions

We release security updates for the current major branch:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| < 1.0.0 | :x:                |

---

## 🔒 Reporting a Vulnerability

If you discover a security vulnerability in **MyHelpDeskAgent**, please report it privately. Do **NOT** create a public GitHub issue.

### Reporting Process
1. Contact the project maintainers directly via email or private security channel.
2. Include a detailed description of the vulnerability, steps to reproduce, and potential impact.
3. Allow up to **48 hours** for an initial response from the security team.

---

## 🔑 IAM & Secret Management Best Practices

To maintain production-level security:

- **Never Commit Credentials**: Never commit GCP service account JSON keys, API keys, or database credentials to source control.
- **Application Default Credentials (ADC)**: Always use ADC (`gcloud auth application-default login`) in local development.
- **Least Privilege IAM**: Assign minimal required IAM roles to the Cloud Run service account:
  - `roles/aiplatform.user` (Vertex AI reasoning engine & memory bank calls)
  - `roles/datastore.user` (Firestore read/write access)
  - `roles/storage.objectViewer` / `roles/storage.objectCreator` (Cloud Storage media access)
- **HTTPS Enforcement**: Ensure all public endpoints enforce TLS 1.2+ / HTTPS (handled automatically by Google Cloud Run).
