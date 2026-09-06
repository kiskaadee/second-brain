# 🎬 MagNetFlix

## 📌 Project Overview
MagNetFlix is an integrated media application designed for exploring, streaming, and indexing media content.

---

## 🎯 Architecture & Components
- **Frontend / Client**: Web UI for browsing media catalog, managing queues, and playback.
- **Backend Services**: API layer, scrapers/indexers, metadata fetchers (TMDB/OMDb), and torrent client bridge.
- **Data Persistence**: Database storage for library states, watch progress, and torrent sessions.

---

## 📋 Roadmaps & Action Items
- [ ] Decouple into a standalone Git repository with isolated Docker build files.
- [ ] Configure GitHub Actions / Gitea Actions to build container images on release.
- [ ] Define declarative Traefik reverse proxy routing (`magnetflix.roadtotech.me`).
- [ ] Implement healthcheck endpoints and integrate with `appctl`.
