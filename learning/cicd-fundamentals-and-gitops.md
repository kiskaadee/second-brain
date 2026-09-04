# 🔄 CI/CD Fundamentals & GitOps Architecture

## 🎯 What is CI/CD?

Continuous Integration (CI) and Continuous Delivery/Deployment (CD) form the backbone of modern software engineering. They automate the lifecycle of building, testing, packaging, and deploying software from Git repositories to production environments.

```
┌──────────────────────────────────────────────────────────┐
│                   CONTINUOUS INTEGRATION (CI)            │
│  [Code Push / PR] ──► [Lint & Format] ──► [Run Tests]    │
│                                  │                       │
│                                  ▼                       │
│                       [Build Container Image]            │
└──────────────────────────────────┬───────────────────────┘
                                   │ (Push artifact)
                                   ▼
┌──────────────────────────────────────────────────────────┐
│                   CONTAINER REGISTRY                     │
│               (GitHub Container Registry / GHCR)         │
│          image: ghcr.io/kiskaadee/homelab-landing:sha-xxx│
└──────────────────────────────────┬───────────────────────┘
                                   │ (Trigger deployment)
                                   ▼
┌──────────────────────────────────────────────────────────┐
│                   CONTINUOUS DELIVERY (CD / GitOps)      │
│  [Production Server] ──► [Pull New Image] ──► [Restart]  │
└──────────────────────────────────────────────────────────┘
```

---

## 🏛️ Core Principles & Invariants

1. **Git as the Single Source of Truth**:
   - Production infrastructure should never be modified ad-hoc via manual SSH sessions unless strictly debugging. Every running service configuration, image tag, and manifest corresponds directly to a committed Git state.
2. **Reproducible & Immutable Artifacts**:
   - Software is packaged into immutable container images (OCI/Docker). Images are built once during CI and promoted across environments without recompilation.
3. **Branch Protection & Separation of Concerns**:
   - `feature/*` or `playground/*` branches: Run linters, unit tests, and security scans on pull request.
   - `main` branch: Production branch. Merging into `main` builds the release image and triggers automated deployment.
4. **Environment Decoupling**:
   - Docker images must **never contain `.env` files, credentials, or production secrets**. Configuration must be injected dynamically at runtime via NixOS SOPS templates and environment files.

---

## ⚖️ Deployment Models: Push vs. Pull (GitOps)

For self-hosted homelabs and edge servers behind NAT/firewalls, there are two primary deployment patterns:

| Metric | Pull Model (GitOps / Watchtower / Diun) 🌟 | Push Model (SSH / Deploy Key) |
| :--- | :--- | :--- |
| **Inbound Network Exposure** | 🔒 **Zero** (No open SSH ports or inbound firewall rules) | ⚠️ Requires exposing SSH or tunneling through VPN |
| **Secret Surface** | 🔒 GitHub Actions holds no server credentials | ⚠️ Requires GitHub Actions to hold SSH private keys |
| **Reconciliation Mechanism** | Background daemon polls GHCR or receives webhook | GitHub Actions connects over SSH to run deploy scripts |
| **Rollback Mechanism** | Pin image tag in `app.yaml` / compose manifest | Run SSH rollback script or revert commit |
| **Homelab Suitability** | 🏆 **Gold Standard** for home servers behind dynamic IPs | Best for cloud VPS with static IPs & bastion hosts |

---

## 🛠️ Production-Ready GitHub Actions Workflow Template

Below is a standard workflow (`.github/workflows/ci-cd.yml`) for homelab micro-services:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    name: Code Quality & Unit Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python Runtime
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install Dependencies & Linters
        run: |
          pip install ruff pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run Linters (Code Formatting & Errors)
        run: ruff check .

      - name: Run Unit Tests
        run: pytest

  build-and-publish:
    name: Build & Publish OCI Container
    needs: lint-and-test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry (GHCR)
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 🔒 Security Best Practices Checklist

- [ ] **Non-Root Execution**: Ensure containers run as non-root (`user: 1000:1000`).
- [ ] **Layer Caching**: Utilize GitHub Actions Cache (`type=gha`) to keep builds under 2 minutes.
- [ ] **Dual Tagging**: Always tag images with both `:latest` and the short commit SHA (`:${{ github.sha }}`) to enable instant rollbacks.
- [ ] **Zero Hardcoded Secrets**: Ensure `.dockerignore` excludes `.env`, `*.key`, `*.sqlite3`, and `secrets/`.
- [ ] **Automated Scanning**: Use Diun or Trivy in pipelines to detect vulnerable upstream base images.
