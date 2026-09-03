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
  - Add domain to chosen DNS manager.
  - Create wildcard record: `*.roadtotech.me` ➔ Target WAN IP.
  - Verify DNS resolution via `dig roadtotech.me +short` and `dig test.roadtotech.me +short`.
- [ ] **Step 2: Update Declarative NixOS Configuration**
  - `hosts/desktop/homeserver.nix`: Change `DOMAIN` to `"roadtotech.me"`.
  - `hosts/desktop/traefik-deployments.nix`: Update `DOMAIN_SUFFIX` and subdomain variables (`DOCS_DOMAIN`, `GITEA_DOMAIN`, etc.).
  - `hosts/desktop/secrets.yaml`: Update DDNS domain variable if stored in SOPS.
- [ ] **Step 3: Traefik & SSL Validation**
  - Trigger Traefik reload/restart.
  - Inspect Traefik logs to confirm Let's Encrypt DNS-01 challenge completion for `roadtotech.me` and `*.roadtotech.me`.
- [ ] **Step 4: Authelia & Cookie Verification**
  - Authenticate against `https://auth.roadtotech.me`.
  - Verify SSO forward-auth across subdomains (`gitea.roadtotech.me`, `jellyfin.roadtotech.me`, etc.).
