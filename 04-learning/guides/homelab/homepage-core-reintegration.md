---
type: guide
project: homelab
tags:
  - operations
  - architecture
  - homelab
  - homepage
  - core
  - dashboard
---

# Walkthrough: Homepage Reintegration into Homelab Core

## Overview
We have extracted **Homepage** (`gethomepage`) from the temporary hybrid `Sites/dashboard` repository and reintegrated it as a first-class service in `Homelab/Core` (`~/Core`).

---

## Changes Implemented

### 1. Reintegrated Clean Configuration
- **Location**: `~/Homelab/Core/config/homepage/`
- **Assets Migrated**:
  - `bookmarks.yaml`: Personal project and social quicklinks
  - `docker.yaml`: Direct connection to `socket-proxy:2375`
  - `settings.yaml`, `widgets.yaml`: Core system info widgets (CPU, Memory, Search)
  - `houston.png`, `houston.svg`, `kubernetes.yaml`, `proxmox.yaml`, `services.yaml.example`
- **Removed Tech Debt**: Completely omitted `custom.js` and `custom.css` (the fragile `MutationObserver` DOM injection hacks used previously to insert the learning Kanban board).

### 2. Core Compose Definition
- **File**: `Homelab/Core/docker-compose.yml`
- Added `homepage` service attached to `socket-net` (for container discovery) and `proxy-net` (for Traefik ingress).
- Configured Traefik TLS router for `dashboard.${DOMAIN}` with automatic HTTP-to-HTTPS redirect.

### 3. Orchestrator (`appctl`) Updates
- **File**: `Homelab/Core/scripts/appctl_engine.py`
  - Registered `homepage` as an official Core service under `get_core_services()`.
  - Updated `cmd_sync_homepage` so `appctl sync` outputs directly to `Core/config/homepage/services.yaml`.
- **File**: `Homelab/Core/.gitignore`
  - Added `config/homepage/services.yaml` to gitignore (since it is compiled dynamically).
- **File**: `Homelab/Core/README.md`
  - Updated manifest documentation to reflect the new services path.

### 4. Structural Tests
- **File**: `Homelab/Core/tests/structural/test_repository_structure.py`
  - Added `config/homepage` to `required_paths`.

---

## Verification & Results

1. **Test Suite**:
   ```bash
   uv run --with pytest --with pyyaml pytest tests
   # 35 passed in 0.18s
   ```
2. **Orchestrator Sync**:
   ```bash
   appctl sync
   # ✨ Homepage synchronized successfully (4 visible apps in 4 groups)
   # 📄 Generated ~/Homelab/Core/config/homepage/services.yaml
   ```
3. **Core Service Listing**:
   ```bash
   appctl list --core
   # homepage is now listed under CORE SERVICE pointing to ~/Homelab/Core
   ```
4. **Compose Syntax Validation**:
   ```bash
   docker compose -f ~/Homelab/Core/docker-compose.yml config
   # Configuration verified valid
   ```
