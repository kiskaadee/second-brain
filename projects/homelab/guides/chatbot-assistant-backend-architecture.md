---
type: guide
project: homelab
---

# 🤖 WhatsApp & Telegram AI Assistant Backend Architecture

## 🎯 Motivation & Objectives
Create a lightweight, self-hosted chatbot backend running on the `roadtotech.me` homelab cluster that serves as a personal AI assistant over messaging channels (Telegram / WhatsApp).

### Primary Capabilities:
1. **Routine Reminders & Scheduled Alerts**: Cron-based triggers for study blocks, habits, and daily check-ins.
2. **AI Engineering Coach & Job Advice**: Context-aware guidance drawing from the resident's curriculum notes (`~/Brain/knowledge`, `~/Brain/journal`, `~/Brain/practice`).
3. **Quick Thought & Note Ingestion**: Send a text or voice memo to the bot to automatically append notes into `~/Brain/journal/` or `~/Brain/knowledge/parking-lot.md`.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    COMMUNICATION CLIENTS                │
│       [ Telegram Mobile App ]   /   [ WhatsApp Web/App ]│
│                   │                         │           │
└───────────────────┼─────────────────────────┼───────────┘
                    │ (Webhook over HTTPS)    │
                    ▼                         ▼
┌─────────────────────────────────────────────────────────┐
│            TRAEFIK EDGE REVERSE PROXY (:443)            │
│         https://bot.roadtotech.me (Wildcard TLS)        │
└───────────────────────────┬─────────────────────────────┘
                            │ (proxy-net)
                            ▼
┌─────────────────────────────────────────────────────────┐
│        HOMELAB ASSISTANT BACKEND (FastAPI / Python)     │
│        ~/Sites/homelab-assistant                        │
│                                                         │
│  ┌────────────────────────┐  ┌────────────────────────┐ │
│  │ APScheduler (Cron/Jobs)│  │ Auth & User Whitelist  │ │
│  │ - Daily Coaching (8am) │  │ - Reject unknown IDs   │ │
│  │ - Evening Journal Promp│  │ - Single-user security │ │
│  └────────────────────────┘  └────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Brain Vault Integration & LLM RAG                  │ │
│  │ - Read access to ~/Brain                           │ │
│  │ - LLM Engine: Ollama / Anthropic Claude / OpenAI   │ │
│  │ - Tool Use: Read notes, add to journal             │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## ⚖️ Telegram Bot API vs. WhatsApp Cloud API

| Metric | Telegram Bot API 🌟 *(Recommended)* | WhatsApp (Cloud API / Baileys) |
| :--- | :--- | :--- |
| **Setup Friction** | ⚡ **30 Seconds**: Chat with `@BotFather`, get API token | ⚠️ High: Requires Meta Developer Account, Business Verification |
| **Cost & Quotas** | 🆓 **100% Free**, unlimited messages | ⚠️ Paid conversation tiers after free monthly threshold |
| **Formatting** | Full Markdown, inline buttons, audio, custom keyboards | Limited markdown, strict template rules for outbound messages |
| **Outbound Cron Messages** | Send messages anytime without pre-approved templates | Requires pre-approved WhatsApp message templates |
| **Security** | Simple user ID whitelist (only responds to your Telegram ID)| Phone number whitelist |

---

## 🚀 Step-by-Step Implementation Roadmap

### Phase 1: Microservice Scaffolding (`~/Sites/homelab-assistant`)
* FastAPI application with `python-telegram-bot` (or `aiogram`).
* Secure webhook endpoint: `POST https://bot.roadtotech.me/webhook/telegram`.
* User ID whitelist middleware: Ignore and drop any message not originating from your authorized Telegram User ID.

### Phase 2: APScheduler Proactive Notifications
* Schedule recurring cron jobs:
  - **08:00 AM**: Daily focus milestone + morning coaching question.
  - **09:00 PM**: Evening reflection reminder.

### Phase 3: Brain Vault Tools & RAG
* Connect the assistant with read/write access to `/home/kiskaadee/Brain`:
  - `/note <text>`: Appends entry to `~/Brain/journal/daily/YYYY-MM-DD.md`.
  - `/ask <question>`: RAG search across `~/Brain/knowledge` to answer questions about past study notes.
