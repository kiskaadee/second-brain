---
type: guide
project: homelab
tags:
  - homelab
  - appctl
  - traefik
  - docker
  - onboarding
---

# 🚀 Onboarding a New Application to the Homelab

This guide provides the complete, step-by-step procedure for deploying a new web service into the `roadtotech.me` homelab ecosystem, integrating it with the **Traefik** edge proxy, **Authelia SSO**, and the **`appctl`** orchestration tool.

---

## 🏗️ The 4-Step Onboarding Workflow

Deploying a new application consists of 4 steps:
1. **Create the application repository in `~/Sites/<app>`**
2. **Author the `app.yaml` manifest**
3. **Author the `docker-compose.yml` with Traefik routing labels**
4. **Deploy and verify using `appctl`**

---

## Step 1: Create the Project Repository

All user applications reside in independent repositories under `/home/kiskaadee/Sites/`:

```bash
mkdir -p ~/Sites/homelab-myapp
cd ~/Sites/homelab-myapp
git init -b main
```

---

## Step 2: Author the `app.yaml` Manifest

Create `~/Sites/homelab-myapp/app.yaml`. This file describes your application metadata, CLI aliases, and presentation card for the Homepage dashboard:

```yaml
name: "myapp"
aliases:
  - "my-app"
  - "custom-app"
domain: "myapp.roadtotech.me"
description: "My New Self-Hosted Web Application"
visible: true        # Set to true to display on Homepage dashboard
auth: true           # Indicates Authelia protection is enabled

networks:
  - proxy-net

env:
  CUSTOM_SETTING: "standard_value"

homepage:
  title: "My App"
  group: "Tools & Utilities" # Dashboard category
  icon: "custom.png"         # Icon name or URL
  container: "myapp"
  weight: 40                 # Sort order in the dashboard

deployment:
  branch: "main"
  actions:
    - git_pull
    - compose_up
```

---

## Step 3: Author the `docker-compose.yml`

Create `~/Sites/homelab-myapp/docker-compose.yml`. Applications connect to Traefik via the external `proxy-net` Docker network.

### Example: Application with Authelia SSO Protection (`auth: true`)

```yaml
services:
  myapp:
    image: myapp/image:latest
    container_name: myapp
    restart: unless-stopped
    networks:
      - proxy-net
    environment:
      - PORT=8080
      - DOMAIN_SUFFIX=${DOMAIN_SUFFIX:-roadtotech.me}
    labels:
      - "traefik.enable=true"
      
      # 1. Secure HTTPS Entrypoint
      - "traefik.http.routers.myapp.rule=Host(`myapp.${DOMAIN_SUFFIX:-roadtotech.me}`)"
      - "traefik.http.routers.myapp.entrypoints=websecure"
      - "traefik.http.routers.myapp.tls=true"
      - "traefik.http.routers.myapp.service=myapp-svc"
      
      # 2. Attach Authelia SSO ForwardAuth Middleware
      - "traefik.http.routers.myapp.middlewares=authelia-auth@docker"

      # 3. HTTP to HTTPS Automatic Redirect Router
      - "traefik.http.routers.myapp-red.rule=Host(`myapp.${DOMAIN_SUFFIX:-roadtotech.me}`)"
      - "traefik.http.routers.myapp-red.entrypoints=web"
      - "traefik.http.routers.myapp-red.middlewares=https-redirect@docker"

      # 4. Target Service Port (inside the container)
      - "traefik.http.services.myapp-svc.loadbalancer.server.port=8080"

networks:
  proxy-net:
    name: ${PROXY_NETWORK:-proxy-net}
    external: true
```

> **Note on Public Apps**: If your app has its own native authentication (like Jellyfin or Gitea) or is public, simply omit the `authelia-auth@docker` middleware label.

---

## Step 4: Deploy and Verify with `appctl`

1. Validate the Compose syntax:
   ```bash
   appctl config myapp
   ```

2. Start the application stack:
   ```bash
   appctl up myapp
   ```
   *`appctl` automatically injects shared environment variables from `/run/secrets/rendered/traefik-deployments.env` and triggers `appctl sync` to register the new card in Homepage.*

3. Inspect running status and logs:
   ```bash
   appctl info myapp
   appctl logs myapp
   ```

4. Verify in the browser:
   Navigate to `https://myapp.roadtotech.me`. Traefik will negotiate a wildcard certificate automatically, and Authelia will prompt for credentials if gated.
