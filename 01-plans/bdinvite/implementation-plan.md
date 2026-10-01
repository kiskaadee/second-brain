---
type: plan
status: completed
project: bdinvite
tags:
  - bdinvite
  - react
  - fastapi
  - traefik
  - deployment
  - birthday
---

# Birthday Invitation App — Implementation Plan

## Goal

Build a complete interactive birthday invitation application (`bdinvite`) with:

- **Guest experience**: A visually rich, mobile-first invitation with animated golden bokeh particles, RSVP form, countdown timer, and map preview — served publicly at `demos.roadtotech.me/birthday/invite`
- **Admin dashboard**: A simple RSVP management and invitation configuration editor, protected by Authelia — served at `demos.roadtotech.me/birthday/admin`
- **Backend**: Lightweight FastAPI service with SQLite (WAL mode), Pydantic validation, and a clean API contract

Working directory: `Sites/bdinvite` (forge: [bdinvite](https://gitea.roadtotech.me/kiskaadee/bdinvite))

---

## User Review Required

> [!IMPORTANT]
> **New infrastructure**: `demos.roadtotech.me` does not currently exist in the homelab. This plan creates Traefik routing for it via docker-compose labels. The wildcard DNS (`*.roadtotech.me`) and TLS certificate already cover it — no Core/NixOS changes needed.

> [!IMPORTANT]
> **Authelia split routing**: The admin path (`/birthday/admin/*`) will be Authelia-protected via a higher-priority Traefik router. The public path (`/birthday/*`) will be unprotected. Both route to the same container. This is a pattern not yet used in the homelab (all current apps use full-domain Authelia protection or none), so deployment verification is critical.

> [!WARNING]
> **Static map preview**: The plan uses a static map tile image URL stored in configuration (`map_preview_url`). You'll need to generate or source this image for the actual venue. During development, a placeholder will be used.

---

## Resolved Decisions (from grill-me)

| Decision | Choice |
|---|---|
| Frontend framework | React + Vite + TypeScript |
| Styling | CSS Modules |
| Particle rendering | Canvas 2D |
| Typography | Google Fonts (Great Vibes / Alex Brush + Montserrat) |
| Container architecture | Single container (multi-stage: Node build → Python runtime) |
| Database | SQLite with WAL mode, volume-mounted |
| Authentication | Authelia-only (ForwardAuth at Traefik level) |
| Routing | Path-based on `demos.roadtotech.me/birthday/*` |
| Traefik split | Two routers: public (no auth) + admin (Authelia) |
| SPA routing | React Router v6 with `basename=/birthday` |
| CTA transition | Smooth scroll + fade |
| Countdown format | `DD : HH : MM : SS` with state transitions |
| Map preview | Static tile image in circular treatment, linking to `mapUrl` |
| Duplicate detection | Normalized phone number uniqueness |
| Phone validation | Colombian format (10 digits, starts with 3, optional +57) |
| Guest +1 | Not supported in v1 |
| Config management | Server-managed (DB-stored, admin-editable, API-served) |
| Admin edit scope | Flat form with text preview; visual design is code-only |
| CSV export | Included in v1 |
| Working directory | `Sites/bdinvite` (canonical) |

---

## Proposed Changes

### P0 — Project Scaffolding & Infrastructure

#### [NEW] `app.yaml`

The `appctl` manifest for service identity and deployment:

```yaml
name: "bdinvite"
aliases:
  - "birthday"
  - "invite"
domain: "demos.roadtotech.me"
description: "Interactive Digital Birthday Invitation with RSVP"
visible: true
auth: false  # Public route exists; Authelia applied selectively via labels
networks:
  - proxy-net
env:
  BASE_PATH: "/birthday"
homepage:
  title: "Birthday Invite"
  group: "Applications"
  icon: "party.png"
  container: "bdinvite"
  weight: 30
```

#### [NEW] `docker-compose.yml`

Single-container deployment with split Traefik routing:

```yaml
services:
  bdinvite:
    build: .
    container_name: bdinvite
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    environment:
      - BASE_PATH=/birthday
    networks:
      - proxy-net
    labels:
      - "diun.enable=false"
      - "traefik.enable=true"

      # ── Public router (invitation + API) ──
      - "traefik.http.routers.bdinvite-public.rule=Host(`${SERVICE_DOMAIN:-demos.roadtotech.me}`) && PathPrefix(`/birthday`)"
      - "traefik.http.routers.bdinvite-public.entrypoints=websecure"
      - "traefik.http.routers.bdinvite-public.tls=true"
      - "traefik.http.routers.bdinvite-public.priority=10"
      - "traefik.http.routers.bdinvite-public.service=bdinvite-svc"

      # ── Admin router (Authelia-protected) ──
      - "traefik.http.routers.bdinvite-admin.rule=Host(`${SERVICE_DOMAIN:-demos.roadtotech.me}`) && PathPrefix(`/birthday/admin`)"
      - "traefik.http.routers.bdinvite-admin.entrypoints=websecure"
      - "traefik.http.routers.bdinvite-admin.tls=true"
      - "traefik.http.routers.bdinvite-admin.priority=20"
      - "traefik.http.routers.bdinvite-admin.middlewares=authelia-auth@docker"
      - "traefik.http.routers.bdinvite-admin.service=bdinvite-svc"

      # ── HTTP → HTTPS redirect ──
      - "traefik.http.routers.bdinvite-red.rule=Host(`${SERVICE_DOMAIN:-demos.roadtotech.me}`) && PathPrefix(`/birthday`)"
      - "traefik.http.routers.bdinvite-red.entrypoints=web"
      - "traefik.http.routers.bdinvite-red.middlewares=https-redirect@docker"

      # ── Service target ──
      - "traefik.http.services.bdinvite-svc.loadbalancer.server.port=8000"

networks:
  proxy-net:
    external: true
```

#### [NEW] `Dockerfile`

Multi-stage build: Node (build React) → Python (serve with FastAPI):

```dockerfile
# ── Stage 1: Build React frontend ──
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python runtime ──
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

COPY backend/ .
COPY --from=frontend-build /build/dist ./static

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### [NEW] `.gitignore`

```gitignore
# Dependencies
frontend/node_modules/
backend/__pycache__/
backend/*.pyc

# Build output
frontend/dist/

# Data
data/

# Environment
.env
*.env.local

# IDE
.vscode/
.idea/
```

---

### P1 — Backend (FastAPI + SQLite)

Directory: `backend/`

```text
backend/
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, lifespan, static mount
│   ├── config.py         # Pydantic Settings
│   ├── database.py       # SQLite engine, session, Base
│   ├── models.py         # SQLAlchemy models (RSVP, InvitationConfig)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── rsvp.py       # POST /api/rsvp
│   │   ├── config.py     # GET /api/config, PUT /api/config
│   │   └── admin.py      # GET /api/admin/rsvps, GET /api/admin/export
│   └── services/
│       ├── __init__.py
│       ├── rsvp.py       # RSVP business logic + phone normalization
│       └── config.py     # Config CRUD + seed defaults
```

#### [NEW] `backend/pyproject.toml`

```toml
[project]
name = "bdinvite"
version = "0.1.0"
description = "Birthday Invitation RSVP Backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[dependency-groups]
dev = [
    "httpx>=0.27.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

#### Database Models

**RSVP table** (`rsvps`):

| Column | Type | Constraints |
|---|---|---|
| `id` | INTEGER | PK, autoincrement |
| `name` | TEXT | NOT NULL |
| `phone` | TEXT | NOT NULL, UNIQUE (normalized) |
| `email` | TEXT | nullable |
| `created_at` | DATETIME | NOT NULL, default=utcnow |

**InvitationConfig table** (`invitation_config`):

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | PK (always 1 — singleton row) |
| `honoree_name` | TEXT | "Isabelle Snow" |
| `event_date` | TEXT | "2026-10-28" |
| `event_time` | TEXT | "19:00" |
| `event_timezone` | TEXT | "America/Bogota" |
| `title` | TEXT | "Birthday Party" |
| `invitation_text` | TEXT | "You're invited to the birthday party honoring" |
| `address_name` | TEXT | "Fresco Ristorante" |
| `address_lines` | TEXT | "514 S Brand Blvd\nGlendale, CA 91204" |
| `map_preview_url` | TEXT | Static map tile image URL |
| `map_url` | TEXT | Google Maps link |
| `rsvp_heading` | TEXT | "¿Nos vemos?" |
| `rsvp_cta` | TEXT | "CONFIRMA TU ASISTENCIA" |
| `submit_label` | TEXT | "TE VEO AHÍ" |
| `msg_success` | TEXT | "¡Perfecto! Tu asistencia ha sido confirmada." |
| `msg_duplicate` | TEXT | "Parece que ya tenemos tus datos registrados." |
| `msg_error` | TEXT | "No pudimos registrar tu asistencia. Inténtalo nuevamente." |
| `updated_at` | DATETIME | |

#### API Endpoints

All API routes are mounted under `/birthday/api/`:

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/birthday/api/config` | Public | Serves invitation configuration to guest frontend |
| `POST` | `/birthday/api/rsvp` | Public | Submit RSVP (name, phone, email?) |
| `GET` | `/birthday/api/admin/rsvps` | Authelia | List all RSVPs (with optional `?search=` query param) |
| `GET` | `/birthday/api/admin/export` | Authelia | Download CSV of all RSVPs |
| `GET` | `/birthday/api/admin/config` | Authelia | Get full config (same as public, but admin context) |
| `PUT` | `/birthday/api/admin/config` | Authelia | Update invitation configuration |

#### API Response Contract

**POST `/birthday/api/rsvp`** request:
```json
{
  "name": "Andrés García",
  "phone": "300 123 4567",
  "email": "andres@example.com"
}
```

**Responses** (all use a `result` discriminator):

```json
// 201 Created — Success
{ "result": "SUCCESS", "name": "Andrés García" }

// 409 Conflict — Duplicate
{ "result": "DUPLICATE" }

// 422 Unprocessable — Validation
{ "result": "VALIDATION_ERROR", "errors": { "phone": "Formato de teléfono inválido" } }

// 500 — Server error
{ "result": "ERROR" }
```

#### Phone Normalization Logic

```python
import re

def normalize_phone(raw: str) -> str:
    """
    Normalize Colombian phone numbers.
    Strips +57 prefix, spaces, dashes, parentheses.
    Returns 10-digit number starting with 3.
    """
    digits = re.sub(r'[^\d]', '', raw)
    if digits.startswith('57') and len(digits) == 12:
        digits = digits[2:]
    if len(digits) != 10 or not digits.startswith('3'):
        raise ValueError("Formato de teléfono inválido")
    return digits
```

#### Admin Auth Guard

Admin endpoints validate the `Remote-User` header (injected by Authelia ForwardAuth):

```python
from fastapi import Header, HTTPException

def require_admin(remote_user: str | None = Header(None, alias="Remote-User")):
    if not remote_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return remote_user
```

#### SPA Catch-All

FastAPI mounts the built React app as static files and provides a catch-all for client-side routing:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# API routes first (registered before catch-all)
app.include_router(rsvp_router, prefix="/birthday/api")
app.include_router(admin_router, prefix="/birthday/api/admin")
app.include_router(config_router, prefix="/birthday/api")

# Static assets (JS, CSS, images)
app.mount("/birthday/assets", StaticFiles(directory="static/assets"), name="assets")

# SPA catch-all: any /birthday/* path serves index.html
@app.get("/birthday/{full_path:path}")
async def spa_catch_all(full_path: str):
    return FileResponse("static/index.html")
```

---

### P2 — Frontend: Guest Invitation (React + Vite + TypeScript)

Directory: `frontend/`

```text
frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── index.html
├── public/
│   └── (static assets)
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   └── client.ts              # fetch wrapper for /birthday/api/*
│   ├── types/
│   │   └── config.ts              # InvitationConfig TypeScript interface
│   ├── hooks/
│   │   ├── useConfig.ts           # Fetch & cache invitation config
│   │   ├── useCountdown.ts        # Live countdown against event datetime
│   │   └── useRsvpForm.ts         # Form state, validation, submission
│   ├── invitation/
│   │   ├── Invitation.tsx         # Main invitation composition
│   │   ├── InvitationContent.tsx  # Title, honoree, date/time display
│   │   ├── ParticleBackground.tsx # Canvas 2D bokeh particles
│   │   ├── RsvpCta.tsx            # "CONFIRMA TU ASISTENCIA ↓"
│   │   ├── RsvpForm.tsx           # Name, phone, email fields + submit
│   │   ├── RsvpResult.tsx         # Success / Duplicate / Error states
│   │   ├── Countdown.tsx          # "TE VEO EN DD:HH:MM:SS"
│   │   └── MapPreview.tsx         # Circular map preview + link
│   ├── admin/
│   │   ├── AdminLayout.tsx        # Dashboard shell (header, nav)
│   │   ├── RsvpTable.tsx          # RSVP list with search + count
│   │   └── ConfigEditor.tsx       # Invitation config form + preview
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── Field.tsx
│   │   └── Spinner.tsx
│   └── styles/
│       ├── global.module.css
│       ├── invitation.module.css
│       ├── particles.module.css
│       ├── rsvp.module.css
│       ├── result.module.css
│       └── admin.module.css
```

#### Vite Configuration

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/birthday/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  server: {
    proxy: {
      '/birthday/api': 'http://localhost:8000',
    },
  },
});
```

#### React Router Setup

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter basename="/birthday">
      <Routes>
        {/* Guest routes */}
        <Route path="/invite" element={<Invitation />} />

        {/* Admin routes */}
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<RsvpTable />} />
          <Route path="config" element={<ConfigEditor />} />
        </Route>

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/invite" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

### P3 — Guest Experience: Visual Design

#### Color Palette

| Role | Value | Usage |
|---|---|---|
| Background | `#0a0a0a` | Page/invitation base |
| Gold primary | `#d4a843` | Particle glow, accents |
| Gold light | `#f0d68a` | Particle highlights, CTA hover |
| Gold dark | `#8b7332` | Subtle text accents |
| Text primary | `#ffffff` | Headings, body |
| Text secondary | `rgba(255,255,255,0.7)` | Metadata, labels |
| Error | `#e74c3c` | Validation errors |
| Success | `#d4a843` | Confirmation accent |

#### Typography

```css
/* Script/display — "Birthday Party", honoree name */
@import url('https://fonts.googleapis.com/css2?family=Great+Vibes&display=swap');

/* Geometric sans-serif — metadata, labels, buttons */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
```

| Element | Font | Weight | Size (mobile) | Tracking |
|---|---|---|---|---|
| Title ("Birthday Party") | Great Vibes | 400 | ~3rem | normal |
| Invitation text | Montserrat | 300 | 0.85rem | 0.2em |
| Honoree name | Great Vibes | 400 | ~2.5rem | normal |
| Date/time | Montserrat | 500 | 1.2rem | 0.15em |
| CTA | Montserrat | 400 | 0.8rem | 0.25em |
| Form labels | Montserrat | 300 | 0.75rem | 0.15em |
| Result heading | Montserrat | 600 | 1.5rem | 0.1em |
| Countdown digits | Montserrat | 300 | 1.8rem | 0.05em |

#### Invitation Layout (Mobile-First)

```css
.invitation {
  width: min(100%, 480px);
  min-height: 100vh;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}
```

The invitation is a single scrollable composition:

```text
┌─────────────────────────────┐
│                             │
│    [ParticleBackground]     │ ← Canvas, position: fixed, z-index: 0
│                             │
│ ┌─────────────────────────┐ │
│ │                         │ │
│ │     Birthday Party      │ │ ← Great Vibes, ~3rem
│ │                         │ │
│ │   YOU'RE INVITED TO     │ │ ← Montserrat 300, tracked
│ │   THE BIRTHDAY PARTY    │ │
│ │      HONORING           │ │
│ │                         │ │
│ │    Isabelle Snow        │ │ ← Great Vibes, ~2.5rem
│ │                         │ │
│ │  FRIDAY | OCT 28 | 7PM │ │ ← Montserrat 500, tracked
│ │                         │ │
│ │  CONFIRMA TU ASISTENCIA │ │ ← CTA (interactive)
│ │           ↓             │ │
│ │                         │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │ ← scroll target
│ │                         │ │
│ │      ¿NOS VEMOS?       │ │
│ │                         │ │
│ │   [name field]          │ │
│ │   [phone field]         │ │
│ │   [email field]         │ │
│ │                         │ │
│ │     TE VEO AHÍ         │ │
│ │                         │ │
│ └─────────────────────────┘ │
│                             │
│ ┌─────────────────────────┐ │ ← replaces form on submit
│ │                         │ │
│ │      ¡PERFECTO!         │ │
│ │                         │ │
│ │  Tu asistencia ha sido  │ │
│ │      confirmada.        │ │
│ │                         │ │
│ │   Gracias, Andrés.      │ │
│ │                         │ │
│ │          ·              │ │
│ │          ·              │ │
│ │     TE VEO EN           │ │
│ │   12 : 04 : 37 : 22    │ │
│ │                         │ │
│ │          ·              │ │
│ │                         │ │
│ │       ╭──────╮          │ │ ← circular map preview
│ │     ╭─┤      ├─╮       │ │    ~140px, clip-path: circle()
│ │    │  │  MAP │  │       │ │
│ │     ╰─┤      ├─╯       │ │
│ │       ╰──────╯          │ │
│ │                         │ │
│ │    VER UBICACIÓN ↗      │ │ ← link to mapUrl
│ │                         │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

#### Particle Background Specification

Canvas implementation details:

```typescript
interface Particle {
  x: number;
  y: number;
  radius: number;       // 2–12px
  opacity: number;       // 0.1–0.6
  blur: number;          // 2–15px (via ctx.shadowBlur)
  goldIntensity: number; // 0–1 (hue shift between warm/cool gold)
  vx: number;            // -0.15 to 0.15 px/frame
  vy: number;            // -0.15 to 0.15 px/frame
  twinkleSpeed: number;  // 0.005–0.02
  twinklePhase: number;  // 0–2π
}
```

Spatial distribution uses a weighted probability that concentrates particles in the upper-left and lower-right quadrants:

```typescript
function generatePosition(width: number, height: number): [number, number] {
  // Bias toward upper-left and lower-right corners
  const bias = Math.random();
  if (bias < 0.4) {
    // Upper-left quadrant
    return [Math.random() * width * 0.5, Math.random() * height * 0.4];
  } else if (bias < 0.8) {
    // Lower-right quadrant
    return [width * 0.5 + Math.random() * width * 0.5, height * 0.6 + Math.random() * height * 0.4];
  } else {
    // Sparse center/other areas
    return [Math.random() * width, Math.random() * height];
  }
}
```

Particle count: ~120 on desktop, ~80 on mobile (based on `window.innerWidth`).

`prefers-reduced-motion`: particles are rendered once as a static frame, animation loop does not run.

#### Countdown Hook

```typescript
function useCountdown(eventDate: string, eventTime: string, timezone: string) {
  // 1. Construct target: "2026-10-28T19:00:00" in America/Bogota
  // 2. Convert to UTC milliseconds using Intl.DateTimeFormat or manual offset
  //    (Colombia = UTC-5, no DST, so offset is always -5h)
  // 3. Calculate: target - Date.now()
  // 4. Return { days, hours, minutes, seconds, state }
  //    state: 'counting' | 'in_progress' | 'finished'
  // 5. Update every second via setInterval
}
```

States:
- `counting`: `TE VEO EN 12 : 04 : 37 : 22`
- `in_progress`: `EVENTO EN CURSO`
- `finished`: `EVENTO FINALIZADO`

#### Map Preview Component

```tsx
function MapPreview({ previewUrl, mapUrl }: { previewUrl: string; mapUrl: string }) {
  return (
    <a href={mapUrl} target="_blank" rel="noopener noreferrer" className={styles.mapLink}>
      <div className={styles.mapCircle}>
        <img src={previewUrl} alt="Ubicación del evento" />
      </div>
      <span className={styles.mapLabel}>VER UBICACIÓN ↗</span>
    </a>
  );
}
```

CSS for circular treatment:
```css
.mapCircle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid rgba(212, 168, 67, 0.3);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.mapLink:hover .mapCircle {
  transform: scale(1.05);
  border-color: rgba(212, 168, 67, 0.6);
}
```

---

### P4 — Frontend: Admin Dashboard

The admin dashboard is a clean, functional interface. No invitation visual effects.

#### Admin Layout

```text
┌──────────────────────────────────────────────────┐
│ 🎂 RSVP Dashboard                      [Config] │
├──────────────────────────────────────────────────┤
│                                                  │
│  Respuestas: 37                     [Descargar]  │
│                                                  │
│  Buscar: [________________________]              │
│                                                  │
│  ┌────────────┬──────────────┬───────┬─────────┐ │
│  │ Nombre     │ Teléfono     │ Email │ Fecha   │ │
│  ├────────────┼──────────────┼───────┼─────────┤ │
│  │ Ana García │ 300 123 4567 │ ana@… │ Sep 30  │ │
│  │ Carlos P.  │ 311 987 6543 │ —     │ Sep 29  │ │
│  └────────────┴──────────────┴───────┴─────────┘ │
│                                                  │
└──────────────────────────────────────────────────┘
```

#### Config Editor

```text
┌──────────────────────────────────────────────────┐
│ 🎂 Configuración                     [← Volver] │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌─── Editar ──────────────────────────────────┐ │
│  │                                             │ │
│  │  Nombre del homenajeado                     │ │
│  │  [Isabelle Snow                        ]    │ │
│  │                                             │ │
│  │  Fecha del evento                           │ │
│  │  [2026-10-28]                               │ │
│  │                                             │ │
│  │  Hora         Zona horaria                  │ │
│  │  [19:00]      [America/Bogota       ]       │ │
│  │                                             │ │
│  │  Texto de invitación                        │ │
│  │  [You're invited to the birthday...]        │ │
│  │                                             │ │
│  │  Nombre del lugar                           │ │
│  │  [Fresco Ristorante                    ]    │ │
│  │                                             │ │
│  │  Dirección (una línea por línea)            │ │
│  │  [514 S Brand Blvd                     ]    │ │
│  │  [Glendale, CA 91204                   ]    │ │
│  │                                             │ │
│  │  URL preview del mapa                       │ │
│  │  [https://tile.openstreetmap.org/...]       │ │
│  │                                             │ │
│  │  URL del mapa (Google Maps, etc.)           │ │
│  │  [https://www.google.com/maps/...]          │ │
│  │                                             │ │
│  │  ... (CTA, submit label, messages) ...      │ │
│  │                                             │ │
│  │              [Guardar cambios]              │ │
│  │                                             │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  ┌─── Vista previa ───────────────────────────┐  │
│  │                                            │  │
│  │  Birthday Party                            │  │
│  │  You're invited to the birthday party...   │  │
│  │  Isabelle Snow                             │  │
│  │  FRIDAY | OCT 28 | 7:00 PM                │  │
│  │  FRESCO RISTORANTE                        │  │
│  │  514 S Brand Blvd, Glendale, CA 91204     │  │
│  │                                            │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

The preview is a plain-text rendering of how the fields compose — **not** a visual replica of the invitation with particles and fonts. It shows the content hierarchy so the admin can verify field values before saving.

---

### P5 — Accessibility

| Requirement | Implementation |
|---|---|
| Semantic HTML | `<main>`, `<section>`, `<form>`, `<h1>`–`<h3>`, `<label>`, `<button>` |
| Keyboard CTA | CTA is a `<button>` with `tabindex`, visible `:focus-visible` ring |
| Keyboard form | Standard form tab order, `<label htmlFor>` associations |
| Focus states | Gold outline ring on interactive elements |
| Text contrast | White on `#0a0a0a` exceeds WCAG AAA (21:1) |
| aria-live | `<div aria-live="polite">` wraps submission result messages |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` → static particles, no scroll animation |
| Error messages | Inline, associated via `aria-describedby` on the field |

---

## Project File Tree (Complete)

```text
Sites/bdinvite/
├── app.yaml
├── docker-compose.yml
├── Dockerfile
├── .gitignore
├── README.md
├── specs/
│   └── front.md                    # Existing spec (preserved)
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── rsvp.py
│   │   │   ├── config.py
│   │   │   └── admin.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── rsvp.py
│   │       └── config.py
│   └── tests/
│       ├── __init__.py
│       ├── test_rsvp.py
│       └── test_config.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts
│       ├── types/
│       │   └── config.ts
│       ├── hooks/
│       │   ├── useConfig.ts
│       │   ├── useCountdown.ts
│       │   └── useRsvpForm.ts
│       ├── invitation/
│       │   ├── Invitation.tsx
│       │   ├── InvitationContent.tsx
│       │   ├── ParticleBackground.tsx
│       │   ├── RsvpCta.tsx
│       │   ├── RsvpForm.tsx
│       │   ├── RsvpResult.tsx
│       │   ├── Countdown.tsx
│       │   └── MapPreview.tsx
│       ├── admin/
│       │   ├── AdminLayout.tsx
│       │   ├── RsvpTable.tsx
│       │   └── ConfigEditor.tsx
│       ├── components/
│       │   ├── Button.tsx
│       │   ├── Field.tsx
│       │   └── Spinner.tsx
│       └── styles/
│           ├── global.module.css
│           ├── invitation.module.css
│           ├── particles.module.css
│           ├── rsvp.module.css
│           ├── result.module.css
│           └── admin.module.css
└── data/                            # Volume-mounted, gitignored
    └── bdinvite.db
```

---

## Verification Plan

### Automated Tests

```bash
# Backend unit tests
cd Sites/bdinvite/backend
uv sync --dev
uv run pytest tests/ -v

# Frontend build verification
cd Sites/bdinvite/frontend
npm ci
npm run build    # TypeScript compilation + Vite build
```

Backend tests cover:
- **RSVP submission**: success, duplicate (phone match), validation errors
- **Phone normalization**: `+57 300 123 4567` → `3001234567`, invalid formats rejected
- **Config CRUD**: seed defaults, update, retrieve
- **Admin auth guard**: missing `Remote-User` header returns 401

### Docker Build Verification

```bash
cd Sites/bdinvite
docker compose build
docker compose up -d
# Verify container starts and serves:
curl -s http://localhost:8000/birthday/invite | head -5
curl -s http://localhost:8000/birthday/api/config | python3 -m json.tool
```

### Manual Verification

The user should manually verify after deployment:

1. **Guest flow**: Visit `https://demos.roadtotech.me/birthday/invite`, verify invitation renders with particles, submit RSVP, see success state with countdown and map
2. **Authelia protection**: Visit `https://demos.roadtotech.me/birthday/admin` unauthenticated → redirect to `auth.roadtotech.me`
3. **Admin dashboard**: After Authelia login, verify RSVP table shows the test submission, CSV export works
4. **Config editor**: Edit invitation text, verify the public invitation updates
5. **Duplicate detection**: Submit the same phone number again, verify duplicate message
6. **Responsive**: Test on mobile viewport (Chrome DevTools or actual device)
7. **Reduced motion**: Enable `prefers-reduced-motion` in browser, verify particles are static
8. **Countdown states**: Verify countdown calculates correctly against `America/Bogota` timezone

### Deployment Handoff

After local build verification passes, the deployment handoff will include:
- Exact `appctl` / docker compose commands
- Post-deployment verification commands
- Rollback procedure
