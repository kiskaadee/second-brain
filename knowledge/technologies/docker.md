# Docker & Containerization Notes

## Docker Core Concepts
- **Image:** A read-only template with instructions for creating a Docker container.
- **Container:** A runnable instance of an image. Isolated from other containers and the host.
- **Dockerfile:** A text document containing all the commands a user could call on the command line to assemble an image.
- **Docker Compose:** A tool for defining and running multi-container Docker applications using YAML configuration.

## Multi-stage Builds
- Used to keep final production image sizes small by compiling/building in an initial stage, then copying only the built artifacts into a minimal runtime image.


---
## Docker Volume names

**Question**: I attempted to namespace the PostgreSQL volume because I expected multiple databases to coexist on this machine. Is naming Docker volumes per application considered good practice? What are the recommended conventions for avoiding collisions while still using PostgreSQL's default data directory? 

**Answer**:
Your concern is real, but the solution is different from changing PostgreSQL's internal data directory.

The **container path** should stay:

```text
/var/lib/postgresql/data
```

The **Docker volume name** is where you namespace.

For example:

```yaml
volumes:
  bitetrack_postgres_data:
```

or

```yaml
volumes:
  bitetrack-db-data:
```

Then mount it like:

```yaml
volumes:
  - bitetrack_postgres_data:/var/lib/postgresql/data
```

The volume name is unique within Docker, while the mount point inside the container remains what PostgreSQL expects. That's the conventional approach and avoids collisions between projects without reconfiguring the database itself.

I applied this by adjusting the mount point name for the BiteTrack database mock: 

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    container_name: bitetrack_pgdb
    restart: unless-stopped
    environment:
      - POSTGRES_USER
      - POSTGRES_PASSWORD
      - POSTGRES_DB
    ports:
      - "5432:5432"
    volumes:
      - bitetrack_data:/var/lib/postgresql/data
volumes:
  bitetrack_data:

```

---

## Docker Compose & Container Management Reference

### Container Lifecycle
```bash
# Start service as a detached process:  
docker compose up -d

# Stop the service
docker compose down

# Wipe container: this resets the container state by deleting persistent data
docker compose down -v

# List project containers: 
docker compose ps

# Include stopped containers: 
docker compose ps -a

# Return only container IDs (useful for scripting):
docker compose ps -q
```

### Diagnostics & Internal Connections
*   **Health Check via Container Logs:**
    *   Command: `docker compose logs -f`
    *   Expected success log for PostgreSQL: `database system is ready to accept connections.`
*   **Connect Internally (via `psql`):**
    *   Jump directly into the container and use the built-in PostgreSQL CLI:
    *   Command: `docker exec -it <container_name> psql -U <username> -d <database_name>`

### Connection Configuration
*   **Port Mapping:** `0.0.0.0:5432 -> 5432/tcp` maps host port 5432 to container port 5432.
*   **Connection URL Example:**
    ```python
    DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
    ```
