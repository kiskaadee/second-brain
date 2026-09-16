---
type: discussion
project: homelab
date: 2026-09-15
tags:
  - homelab
  - email
  - stalwart
  - architecture
---

# Mail Server Evaluation for Homelab Core: Why Stalwart is the Modern Standard

## Executive Summary

For modern, resource-conscious homelabs running on NixOS and Docker Compose with LLDAP, **Stalwart Mail Server** is currently the best-in-class choice. It replaces the legacy multi-daemon architecture (Postfix + Dovecot + Rspamd + Redis + MariaDB) with a single, memory-safe Rust binary that uses ~50 MB of RAM while supporting both modern protocols (JMAP) and legacy standards (IMAP/SMTP).

---

## Comparison of Self-Hosted Mail Solutions

| Feature | Stalwart Mail | Mailcow (dockerized) | docker-mailserver | Mail-in-a-Box |
| :--- | :--- | :--- | :--- | :--- |
| **Architecture** | **Single binary (Rust)** | 12–15 microservices | Bundled daemons (Postfix/Dovecot) | Full OS takeover (Ubuntu) |
| **RAM Footprint** | **~50–80 MB** | 3.5–5.0 GB | ~800 MB – 1.5 GB | ~1.5 GB |
| **LLDAP Native Support** |  **First-class directory** |  Via complex LDAP pass-through |  Via dovecot-ldap.conf | ❌ Local SQLite/flat |
| **Protocols** | **JMAP + IMAP4 + SMTP** | IMAP4 + SMTP (SOGo) | IMAP4 + SMTP | IMAP4 + SMTP |
| **Spam / Security Engine** | Built-in Rust engine | Rspamd + ClamAV + Redis | Rspamd / SpamAssassin | SpamAssassin |
| **Traefik Compatibility** |  Seamless | ⚠️ Clashes with external proxy |  Seamless | ❌ Takes over Port 80/443 |
| **Backup Simplicity** | Single data volume + SQLite/S3 | Multiple volumes + MySQL dump | Multiple config & mail volumes | Duplicity backup |

---

## Why Stalwart Fits the Roadtotech Homelab Architecture

### 1. Architectural Synergy with LLDAP
Stalwart was designed with modern directory services in mind. It pairs with LLDAP out of the box:
- Point Stalwart's directory provider to `ldap://lldap:3890` with base DN `dc=roadtotech,dc=me`.
- Accounts created in `users.roadtotech.me` immediately receive mailboxes and authenticate seamlessly.

### 2. Next-Gen JMAP Protocol
In addition to standard IMAP/SMTP for apps like Thunderbird, Apple Mail, and Outlook, Stalwart supports **JMAP** (RFC 8620) — the modern REST/JSON mail protocol created by Fastmail. JMAP provides instant synchronization, push notifications, and consumes 90% less battery and data on mobile devices.

### 3. All-in-One Engine
Traditional mail stacks require maintaining 5+ distinct configuration syntaxes (Postfix `main.cf`, Dovecot `dovecot.conf`, Rspamd Lua rules, OpenDKIM, Sieve). Stalwart unifies SMTP routing, IMAP storage, DKIM signing, ARC, SPF, DMARC validation, and spam filtering into a single declarative configuration file (`stalwart.toml`) or Web Admin UI.

---

## The Reality of Homelab Email Deliverability

When hosting email on a homelab connection (residential or small business ISP):

1. **Inbound Mail (Receiving)**:
   - Works flawlessly. Traefik or direct host port mappings forward inbound Port 25 to Stalwart.
2. **Outbound Mail (Sending)**:
   - **The Challenge**: Almost all residential IP ranges are on Spamhaus's Policy Block List (PBL). Major providers (Gmail, Microsoft 365, Yahoo) reject or quarantine mail sent directly from residential IP pools to prevent malware botnets from spamming.
   - **The Solution (SMTP Relay / Smart Host)**:
     - Configure Stalwart to route outgoing mail through an authenticated SMTP relay:
       - **AWS SES (Simple Email Service)**: Free tier covers 3,000 emails/month; otherwise $0.10 per 10,000 emails.
       - **Brevo (Sendinblue) / SendGrid**: 300 free emails/day.
     - Stalwart manages your DKIM signing locally, so the email is cryptographically signed by `roadtotech.me`, but safely relayed through clean IP pools with 99.9% inbox deliverability.
