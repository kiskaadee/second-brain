---
type: discussion
project: homelab
date: 2026-09-15
tags:
  - homelab
  - email
  - hostinger
  - stalwart
---

# Hostinger Business Email vs. Self-Hosted Stalwart + Relay Architecture

## 1. Architectural Integration Comparison

| Criterion | Stalwart Mail Server (+ Brevo/SES Relay) | Hostinger Business Email (SaaS) |
|---|---|---|
| **Directory Integration** | **Direct LLDAP integration** (`ldap://lldap:3890`). Creating a user in LLDAP automatically provisions their mailbox and credentials. | **None.** Hostinger is a closed proprietary platform; no LDAP, Active Directory, or OIDC sync. Users and passwords must be manually duplicated in Hostinger hPanel. |
| **Authentication & SSO** | **Unified credentials** with Authelia, Jellyfin, Gitea, and Nextcloud. One password across the entire homelab. | **Separate credentials.** Users have an independent Hostinger email password distinct from their homelab login. |
| **Cost** | **$0 / month.** 100% free (Brevo provides 300 free outgoing emails/day; Stalwart stores data on local server NVMe). | **Pay per mailbox.** ~1,900 CO$/mo (~$0.50/mo) intro rate per user, renewing at 4,900 CO$/mo per user (~$1.20/mo). For 5 users, ~$6/mo. |
| **Storage Limits** | **Local disk capacity.** Gigabytes/terabytes limited only by homelab drive storage. | **5 GB per mailbox** (Starter plan). Higher storage tiers cost 3,900–5,900 CO$/mo per user. |
| **Alias & User Limits** | **Unlimited** domains, users, and aliases. | **5 aliases & 5 forwarding rules** per mailbox on Starter plan. |
| **Homelab Service Alerts** | Native local SMTP submission on Docker `proxy-net` (`stalwart:25/587`). | Any homelab app (Gitea, Authelia, Houston) can authenticate to `smtp.hostinger.com:465` to send emails. |
| **Uptime / Power Outages** | Dependent on home power & internet. (If homelab is offline, senders retry automatically for 24–72 hours). | **Cloud-hosted (99.9% uptime).** Mail is received and stored in the cloud regardless of home server status. |
| **Maintenance** | Self-managed container updates, volume backups (`./config/stalwart`). | Fully managed by Hostinger; zero server administration. |

---

## 2. Can We Connect Current Infrastructure to Hostinger?

Yes, in the following ways:

1. **Homelab Notification Outbox (Transactional SMTP):**
   - We can create a dedicated mailbox in Hostinger (e.g. `notifications@roadtotech.me`).
   - Authelia, Gitea, Houston, and Homepage can be configured with Hostinger's SMTP (`smtp.hostinger.com:465`) to dispatch system emails, password resets, and commit notifications.
2. **Dashboard Webmail Integration:**
   - Homepage dashboard (`dashboard.roadtotech.me`) can feature a webmail tile pointing to `https://mail.hostinger.com` (or `webmail.roadtotech.me`).
3. **What Cannot Be Connected:**
   - **LLDAP Sync:** You cannot synchronize LLDAP users or passwords into Hostinger.
   - **Authelia Forward-Auth for Webmail:** Hostinger's webmail runs on Hostinger's infrastructure and cannot be guarded by your local Authelia forward-auth.

---

## 3. Engineering Verdict & Recommendation

- **Stick to Stalwart + Brevo/SES if:**
  The goal is a cohesive, self-hosted homelab ecosystem where LLDAP serves as the single source of truth for identities, passwords, and mailboxes, with unlimited storage and zero ongoing monthly subscription costs.
- **Choose Hostinger Business Email if:**
  You prioritize having email hosted in the cloud with zero maintenance, 24/7 availability independent of home power/internet outages, and don't mind managing users manually in Hostinger's panel and paying the per-mailbox monthly fee.
