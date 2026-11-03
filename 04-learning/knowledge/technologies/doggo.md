---
type: knowledge
status: stable
topics:
  - dns
  - networking
  - doggo
  - troubleshooting
tags:
  - dns
  - networking
  - doggo
  - cli
  - diagnostics
---

# 🐶 `doggo` DNS Diagnostics & Troubleshooting Guide

## Overview

`doggo` is a modern, human-friendly command-line DNS client written in Go. While traditional utilities like `dig` output raw, verbose BIND-style zone records, `doggo` formats responses into clear visual tables, colorful status flags, and structured JSON output.

This makes `doggo` particularly well-suited for interactive network diagnostics, DNS propagation checks, and troubleshooting domain resolution failures.

---

## 1. Spotting Propagation & Local Cache Issues

When updating a DNS record (such as an A or CNAME record), changes take time to propagate across recursive resolvers worldwide due to caching.

### Multi-Resolver Query
Query multiple upstream nameservers simultaneously by separating them with commas:

```bash
# Query local ISP/gateway, Google Public DNS, and Cloudflare simultaneously
doggo roadtotech.me @200.21.200.10,@8.8.8.8,@1.1.1.1
```

### Diagnostic Value
- If your local resolver (`@200.21.200.10`) returns the old IP while public resolvers (`@1.1.1.1` or `@8.8.8.8`) return the new one, the authoritative record is updated correctly; you are merely waiting for local recursive caches to expire.
- If all public resolvers and the authoritative nameserver still serve the old IP, the change was not properly applied at the DNS provider or registrar level.

---

## 2. Tracking TTL (Time to Live) & Cache Invalidation

The `TTL` column indicates the number of seconds a recursive resolver is allowed to retain a record before querying the authoritative nameserver again.

### Monitoring TTL Countdown

```bash
# Query default resolver repeatedly to observe cache expiration
doggo roadtotech.me
```

### Diagnostic Value
- **Observing Invalidation**: Running the command a few seconds apart will show the TTL value counting down (e.g., `298s` $\rightarrow$ `285s` $\rightarrow$ `12s`). When it reaches `0`, the next query pulls fresh records from upstream authority.
- **Root-Cause Analysis**: If an updated record fails to take effect for certain clients, inspecting the TTL explains how long clients are bound to the cached response.

---

## 3. Diagnosing "Website Down" & Nameserver Delegation

When a domain fails to resolve entirely, determine whether the issue is at the application layer, the DNS record level, or nameserver delegation at the registrar.

### Query Nameserver (NS) Records

```bash
# Query authoritative nameservers for the domain
doggo roadtotech.me NS
```

### Diagnostic Value
- **Missing / Empty NS**: If querying `NS` returns an error or no records, check registrar settings: domain registration may be expired, domain status may be on `clientHold`/`serverHold`, or custom nameservers were incorrectly configured.
- **Authoritative Verification**: Once nameservers (e.g., `pam.ns.cloudflare.com`) are known, query them directly with `doggo roadtotech.me @pam.ns.cloudflare.com` to bypass recursive caching and verify authoritative state.

---

## 4. Reading DNS Response Status Codes (RCODEs)

When lookups fail, `doggo` highlights the response code in the `STATUS` column:

| Status Code | Meaning | Common Root Causes & Actions |
| :--- | :--- | :--- |
| `NOERROR` | Success | The nameserver replied successfully and found matching records (or an empty answer if the name exists without that specific record type). |
| `NXDOMAIN` | Non-Existent Domain | The domain or queried hostname does not exist on the authoritative server. Check for spelling errors, missing subdomains, or unconfigured DNS zones. |
| `SERVFAIL` | Server Failure | The resolver failed to obtain an answer. Often caused by broken DNSSEC validation (expired signatures, mismatched DS records at registrar), upstream network timeouts, or circular delegation loops. |
| `REFUSED` | Query Refused | The nameserver refused to process the query. Typically triggered by ACL restrictions (e.g., recursive queries disabled for external IPs) or attempted unauthorized zone transfers (`AXFR`). |

---

## 5. Inspecting Raw DNS Details with JSON Output

Tabular outputs are easy to read but can truncate lengthy strings (such as SPF rules, DKIM public keys, or TLS / SSHFP fingerprints).

### Emitting Structured JSON

```bash
# Inspect long TXT and DKIM validation records
doggo roadtotech.me TXT --output json
```

### Pipe to `jq` for Deep Inspection

```bash
# Filter JSON output for specific answers and strings
doggo roadtotech.me TXT --output json | jq '.responses[].answers'
```

### Diagnostic Value
- Prevents visual truncation of critical security and verification records.
- Allows programmatic validation in CI/CD pipelines, shell scripts, and health-check monitors.

---

## Quick Reference Summary

| Diagnostic Intent | Command Example |
| :--- | :--- |
| Basic A record lookup | `doggo roadtotech.me` |
| Compare resolvers | `doggo roadtotech.me @8.8.8.8,@1.1.1.1` |
| Check mail exchange (MX) | `doggo roadtotech.me MX` |
| Check nameservers (NS) | `doggo roadtotech.me NS` |
| Full raw output in JSON | `doggo roadtotech.me TXT --output json` |
| Query over DNS-over-HTTPS (DoH) | `doggo roadtotech.me @https://cloudflare-dns.com/dns-query` |
