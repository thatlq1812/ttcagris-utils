# Docker Setup Summary

## Overview
All infrastructure services (PostgreSQL, Redis) are now running in Docker containers managed by [noti-service/docker-compose.yml](../noti-service/docker-compose.yml).

## Running Containers

```bash
# Start all infrastructure
cd noti-service
docker-compose up -d

# Check status
docker ps

# Stop all
docker-compose down
```

**Current containers:**
- `dev_postgres` - PostgreSQL 17 on port 5432
- `dev_redis` - Redis 7 on port 6379

## Database Configuration

### Standardized Settings (All Services)

```yaml
database:
  host: "localhost"        # Use localhost when running services on host
  port: 5432
  username: "postgres"
  password: "postgres"     # Standardized password
  ssl_mode: "disable"
```

### Created Databases

1. **centre_auth_service** - For centre-auth-service
2. **notification_service** - For noti-service

### Auto-initialization

Database creation is automated via [scripts/init-db.sh](../scripts/init-db.sh) mounted in docker-compose.yml:

```yaml
volumes:
  - ../scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
```

This script runs automatically on first container start.

## Connection Details

### PostgreSQL

**From Host (Windows):**
```bash
# Using Docker exec
docker exec -it dev_postgres psql -U postgres -d centre_auth_service

# Connection string
postgresql://postgres:postgres@localhost:5432/centre_auth_service
```

**From other Docker containers:**
```yaml
# Use container name as hostname
host: "dev_postgres"
port: 5432
```

### Redis

**From Host:**
```bash
# Test connection
redis-cli -h localhost -p 6379 ping

# Expected: PONG
```

**Connection string:**
```
redis://localhost:6379/0
```

## Migrations

### Centre-Auth-Service

```bash
# Run migrations via Docker
cd centre-auth-service
for f in migrations/*.sql; do
  docker exec -i dev_postgres psql -U postgres -d centre_auth_service < "$f"
done

# Or use make (requires psql in PATH)
make migrate-up
```

### Verify Tables

```bash
docker exec dev_postgres psql -U postgres -d centre_auth_service -c "\dt"
```

**Expected tables:**
- users
- accounts
- refresh_tokens
- otp_verifications
- device_sessions
- farmers
- suppliers
- ekycs
- parcel_lands
- polygon_coordinates
- consent_logs
- consent_policies
- roles
- permissions
- role_permissions
- etc.

## Configuration Files Updated

### 1. [noti-service/docker-compose.yml](../noti-service/docker-compose.yml)

**Changes:**
- PostgreSQL password: `devpass` → `postgres`
- Database name: `product_svc_db` → `postgres` (default, others created by init script)
- Added init-db.sh volume mount
- Healthcheck fixed to use correct user

**Current config:**
```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - ../scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
```

### 2. Service Configurations

All services use consistent database configuration:

**[centre-auth-service/config/config.yaml](../centre-auth-service/config/config.yaml):**
```yaml
database:
  host: "localhost"
  password: "postgres"
  database: "centre_auth_service"
```

**[noti-service/config/config.yml](../noti-service/config/config.yml):**
```yaml
database:
  host: "localhost"
  password: "postgres"
  database: "notification_service"
```

## Quick Commands

### Start Infrastructure

```bash
cd d:/ttcagris/noti-service
docker-compose up -d
```

### Check Health

```bash
# PostgreSQL
docker exec dev_postgres pg_isready -U postgres

# Redis
docker exec dev_redis redis-cli ping

# List databases
docker exec dev_postgres psql -U postgres -c "\l" | grep "_service"
```

### View Logs

```bash
# PostgreSQL logs
docker logs dev_postgres

# Redis logs
docker logs dev_redis

# Follow logs
docker logs -f dev_postgres
```

### Restart Containers

```bash
cd noti-service

# Restart specific container
docker-compose restart postgres

# Restart all
docker-compose restart
```

### Clean Up (CAUTION: Deletes data)

```bash
# Stop and remove containers (keeps volumes)
docker-compose down

# Remove containers AND volumes (destroys all data)
docker-compose down -v
```

## Troubleshooting

### Issue: "connection refused"

**Cause:** Containers not running

**Solution:**
```bash
cd noti-service
docker-compose up -d
docker ps  # Verify running
```

### Issue: "password authentication failed"

**Cause:** Old password cached or config mismatch

**Solution:**
1. Check docker-compose.yml has `POSTGRES_PASSWORD: postgres`
2. Check service configs use `password: "postgres"`
3. Restart containers: `docker-compose restart postgres`

### Issue: "database does not exist"

**Cause:** Init script didn't run

**Solution:**
```bash
# Manually create database
docker exec -it dev_postgres psql -U postgres
CREATE DATABASE centre_auth_service;
CREATE DATABASE notification_service;
\q
```

### Issue: Port already in use

**Cause:** Another service using 5432 or 6379

**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :5432

# Kill the process or change docker-compose port mapping
# Example: "5433:5432" to expose on 5433 instead
```

### Issue: Migrations fail with "psql not found"

**Cause:** Git Bash doesn't have psql in PATH

**Solution:** Use Docker exec method:
```bash
cd centre-auth-service
for f in migrations/*.sql; do
  docker exec -i dev_postgres psql -U postgres -d centre_auth_service < "$f"
done
```

## Network Configuration

**Default Docker network:** `noti-service_default` (created automatically)

**For service-to-service communication:**
```yaml
# Add other services to docker-compose.yml
services:
  centre-auth-service:
    networks:
      - noti-service_default
```

**Or use host network mode:**
```yaml
network_mode: "host"  # Services can use localhost
```

## Next Steps

After infrastructure is running:

1. ✅ Start PostgreSQL & Redis: `cd noti-service && docker-compose up -d`
2. ✅ Verify databases created: `docker exec dev_postgres psql -U postgres -c "\l"`
3. ✅ Run migrations: See "Migrations" section above
4. ▶️ Start centre-auth-service: `cd centre-auth-service && go run cmd/app/main.go`
5. ▶️ Start noti-service: `cd noti-service && go run cmd/main.go`
6. ▶️ Start gateway: `cd app-api-gateway && ./bin/app api`
7. 🧪 Test APIs: Follow [REGISTRATION_FLOW_GUIDE.md](dec17/REGISTRATION_FLOW_GUIDE.md)

## References

- [PORT_ALLOCATION.md](PORT_ALLOCATION.md) - Port strategy and allocation
- [INFRASTRUCTURE_CHECKLIST.md](INFRASTRUCTURE_CHECKLIST.md) - Pre-flight checklist
- [QUICK_SETUP_GUIDE.md](dec17/QUICK_SETUP_GUIDE.md) - Complete setup guide
- [REGISTRATION_FLOW_GUIDE.md](dec17/REGISTRATION_FLOW_GUIDE.md) - API testing guide
