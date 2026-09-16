---
type: guide
project: homelab
tags:
  - homelab
  - email
  - deliverability
  - brevo
  - dns
---

# Mail Deliverability Guide: Solving Dynamic IPs, Missing rDNS (PTR), and Spamhaus PBL

## 1. The Core Problem: Why Residential IPs Land in Spam

Your concern is 100% accurate: **Attempting to send outbound email directly from a residential or dynamic IP to major providers (Gmail, Outlook, Yahoo, Apple) is virtually guaranteed to fail or go to spam.**

Here is what receiving mail servers check when a connection arrives on port 25:

1. **Forward-Confirmed Reverse DNS (FCrDNS / PTR):**
   - The receiving MTA checks the connecting IP (`186.168.147.225`) and looks up its PTR record.
   - It expects the PTR to resolve to the server's FQDN (e.g., `mail.roadtotech.me`), and for `mail.roadtotech.me` to resolve back to that exact same IP.
   - Residential ISPs do not permit custom PTR configuration on consumer dynamic lines; they either return `NXDOMAIN` or a generic residential hostname (e.g., `cpe-186-168-xxx.isp.net`).
2. **Policy Block List (Spamhaus PBL & RBLs):**
   - Almost every residential dynamic IP block in the world is pre-emptively listed on Spamhaus PBL (Policy Block List) and similar spam databases.
   - Major providers (Google, Microsoft) query Spamhaus PBL on the connecting IP. If listed, they reject with `550 5.7.1 Service unavailable; Client host [...] blocked using Spamhaus`.

---

## 2. Inbound vs. Outbound: The Asymmetry of Email

Email delivery is fundamentally asymmetrical:

| Direction | What Happens | Is PTR / rDNS Required? | Is Static IP Required? |
|---|---|---|---|
| **Inbound** (Receiving mail from others) | A sender (e.g. Gmail) looks up your `MX` record (`mail.roadtotech.me`) and connects to your port 25. | **NO**. Your server never presents PTR; you are the *listener*. | **NO**. As long as dynamic DNS (Dynu) points `mail.roadtotech.me` to your current IP, inbound mail arrives normally. |
| **Outbound** (Sending mail to others) | Your server connects to Gmail's port 25 (`gmail-smtp-in.l.google.com`). | **YES**. Gmail inspects *your* connecting IP for valid PTR and PBL status. | **YES**. Sending directly from dynamic residential IP causes immediate rejection. |

---

## 3. The Proven Solutions

There are two production-grade patterns homelabs use to achieve **10/10 deliverability (zero spam flag)** without an enterprise ISP static line:

### Pattern A: The Smart Host Relay (Recommended — Free & No VPS Needed)

Stalwart acts as your complete private mail server (storing emails, providing IMAP/JMAP mailboxes to your phone and computer), but uses an **authenticated outbound relay (Smart Host)** for sending external emails.

```mermaid
flowchart LR
    subgraph Homelab ["Homelab (Dynamic IP)"]
        Client["Email Client<br/>(Thunderbird / Phone)"]
        Stalwart["Stalwart Mail Server<br/>• Stores Mailboxes (IMAP/JMAP)<br/>• Signs with your Domain DKIM"]
    end

    subgraph Outbound ["Smart Host Relay (Static IP + Clean PTR)"]
        Relay["Brevo / Amazon SES<br/>• Static Enterprise IP<br/>• Clean rDNS (PTR)<br/>• SPF: include:spf.brevo.com"]
    end

    subgraph Recipient ["Recipient"]
        Gmail["Gmail / Outlook MTA<br/>Checks: SPF ✓ DKIM ✓ DMARC ✓<br/>Placement: INBOX"]
    end

    Client -->|Submit| Stalwart
    Stalwart -->|Encrypted TLS (587)| Relay
    Relay -->|Delivers| Gmail
```

#### Why This Gives 100% Inbox Placement:
1. **DKIM:** Stalwart signs the outgoing email with your private key for `roadtotech.me`. The cryptographic signature proves you wrote it.
2. **SPF:** Your DNS SPF record includes the relay (`v=spf1 mx include:spf.brevo.com ~all`).
3. **DMARC:** Passes with flying colors because DKIM aligns with `roadtotech.me`.
4. **Connecting IP:** Gmail sees the email coming from the relay's IP (which has clean rDNS and zero PBL listings). Your residential dynamic IP is **never exposed** or penalized.
5. **Cost:**
   - **Brevo (Sendinblue):** Free tier allows **300 emails/day** (9,000/month) with zero cost.
   - **Amazon SES:** **10,000 emails/month** free or $0.10/10k.

---

### Pattern B: The VPS WireGuard Gateway (100% Self-Hosted — ~$3/mo)

If you strictly do not want any third-party relay touching your outbound emails:

```mermaid
flowchart LR
    subgraph Homelab ["Homelab (Dynamic IP)"]
        Stalwart["Stalwart Mail Server"]
    end

    subgraph Cloud ["Cloud VPS ($3/mo - Hetzner / RackNerd)"]
        VPS["VPS Gateway<br/>• Dedicated Static IP<br/>• Custom PTR: mail.roadtotech.me<br/>• WireGuard Tunnel"]
    end

    subgraph Internet ["Public Internet"]
        World["External Mail Servers"]
    end

    Stalwart <==>|Encrypted WireGuard Tunnel| VPS
    VPS <==>|Port 25 (In & Out)| World
```

1. Rent a cheap cloud VPS (Hetzner Cloud ~$3.50/mo or RackNerd ~$15/yr) that provides a static IPv4 and allows setting custom rDNS (PTR).
2. Set the VPS PTR record to `mail.roadtotech.me`.
3. Establish a WireGuard tunnel between the VPS and your homelab server.
4. Route port 25 traffic (both inbound and outbound) through the VPS tunnel.

---

## 4. Summary & Recommendation

- If you don't want to pay for or manage a VPS: **Pattern A (Stalwart + Free Brevo/SES Outbound Relay)** is the gold standard. You get full self-hosted privacy for storage, IMAP, and JMAP, while piggybacking on enterprise deliverability for outbound emails.
- If you want absolute sovereignty without any intermediary: **Pattern B (VPS WireGuard Gateway)** gives you a dedicated static IP and custom PTR for ~$3/month.
