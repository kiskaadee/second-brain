# 🌐 Domain Migration Plan: `arch-services.mywire.org` ➔ `roadtotech.me`

## 🎯 Objective
Migrate all homelab public endpoints, Authelia single sign-on (SSO), Traefik reverse proxy routers, and SSL certificates from Dynu's free subdomain (`arch-services.mywire.org`) to the custom registered domain (`roadtotech.me`).

---

## 🛠️ DNS & Provider Strategies

### Option A: Dynu Custom Domain (Zero Traefik Changes)
1. In Hostinger registrar, set Custom Nameservers: `ns1.dynu.com` ... `ns6.dynu.com`.
2. In Dynu Control Panel, add `roadtotech.me` under DDNS services.
3. Keep Traefik ACME resolver as `provider=dynu` with existing `DYNU_API_KEY`.
4. Update NixOS environment declarations to `DOMAIN = "roadtotech.me"`.

### Option B: Cloudflare DNS (Homelab Industry Standard)
1. In Hostinger registrar, set Cloudflare Nameservers.
2. In Cloudflare, create an `A` record or dynamic DNS updater with API token.
3. Switch Traefik ACME resolver to `provider=cloudflare` with `CF_DNS_API_TOKEN`.

---

## 📋 Implementation Checklist

- [x] **Step 1: DNS Setup & Propagation Verification**
  - Hostinger nameservers delegated to Dynu (`ns1.dynu.com` - `ns6.dynu.com`).
  - Wildcard dynamic DNS configured for `*.roadtotech.me` and apex `roadtotech.me`.
- [x] **Step 2: Declarative NixOS Configuration Updated**
  - `hosts/desktop/homeserver.nix`: Configured `DOMAIN = "roadtotech.me"`.
  - `hosts/desktop/traefik-deployments.nix`: Configured `DOMAIN_SUFFIX = "roadtotech.me"` and `DOCS_PROJECT_PATH = "/home/kiskaadee/Brain"`.
  - Secrets rendered to `/run/secrets/rendered/homeserver.env` and `/run/secrets/rendered/traefik-deployments.env`.
- [x] **Step 3: Traefik & Wildcard SSL Validation**
  - Let's Encrypt DNS-01 wildcard challenge successfully issued certificate for `roadtotech.me` and `*.roadtotech.me`.
  - Validated SNI TLS handshake across all subdomains.
- [x] **Step 4: Authelia & Cookie Verification**
  - ForwardAuth configured and tested for `auth.roadtotech.me`.
