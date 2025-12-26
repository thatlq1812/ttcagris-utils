# Infrastructure Verification Checklist

Run this checklist before starting any services to ensure all dependencies are properly configured.

## ✅ Pre-Setup Checklist

### 1. PostgreSQL Installation & Configuration

**Check if PostgreSQL is installed:**

```bash
# Check version
psql --version

# Expected output: psql (PostgreSQL) 14.x or higher
```

**If not installed:**
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Linux**: `sudo apt-get install postgresql-14` (Ubuntu/Debian)
- **Mac**: `brew install postgresql@14`

**Check if PostgreSQL is running:**

```bash
# All platforms
pg_isready -h localhost -p 5432 -U postgres

# Expected: localhost:5432 - accepting connections
```

**Start PostgreSQL if not running:**

```bash
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl start postgresql

# Mac
brew services start postgresql@14
```

**Verify connection:**

```bash
# Test connection (will prompt for password)
psql -U postgres -h localhost -p 5432 -c "SELECT version();"

# Default password is usually: postgres
```

---

### 2. Redis Installation & Configuration (Optional but Recommended)

**Check if Redis is installed:**

```bash
redis-cli --version

# Expected: redis-cli 6.x or higher
```

**If not installed:**
- **Windows**: Download from https://github.com/microsoftarchive/redis/releases
- **Linux**: `sudo apt-get install redis-server`
- **Mac**: `brew install redis`

**Check if Redis is running:**

```bash
redis-cli ping

# Expected: PONG
```

**Start Redis if not running:**

```bash
# Windows
redis-server

# Linux
sudo systemctl start redis

# Mac
brew services start redis
```

**Verify connection:**

```bash
redis-cli
> ping
PONG
> exit
```

---

### 3. Database Setup

**Run database setup script:**

```bash
# Linux/Mac/Git Bash
cd ttcagris
bash scripts/setup-databases.sh

# Windows Command Prompt
cd ttcagris
scripts\setup-databases.bat
```

**Manual database creation (if script fails):**

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create databases
CREATE DATABASE centre_auth_service;
CREATE DATABASE notification_service;

# List databases to verify
\l

# Exit
\q
```

**Verify databases exist:**

```bash
psql -U postgres -l | grep "_service"

# Expected output:
# centre_auth_service
# notification_service
```

---

### 4. Configuration Verification

**Check all services use same database credentials:**

```bash
# Centre-Auth-Service
grep -A 6 "^database:" centre-auth-service/config/config.yaml

# Should show:
#   password: "postgres"
#   database: "centre_auth_service"

# Notification-Service
grep -A 6 "^database:" noti-service/config/config.yml

# Should show:
#   password: "postgres"
#   database: "notification_service"
```

**Check port allocations:**

```bash
# Gateway config
grep -A 15 "^services:" app-api-gateway/config/config.yaml

# Should show:
#   cas-service: "localhost:50051"
#   notification-service: "localhost:9012"
```

---

### 5. Port Availability Check

**Verify required ports are available:**

```bash
# Check if any service is using our ports
netstat -ano | grep -E ":8080|:50051|:9012|:5432|:6379"

# Expected for fresh setup: Only 5432 (PostgreSQL) and 6379 (Redis) should be in use
```

**If ports are in use, kill processes:**

```bash
# Find process using port (example for 8080)
netstat -ano | findstr :8080

# Kill process (Windows)
taskkill /PID <process_id> /F

# Kill process (Linux/Mac)
kill -9 <process_id>
```

---

### 6. Run Database Migrations

**Centre-Auth-Service:**

```bash
cd centre-auth-service

# Check migration status
make migrate-version

# Run all migrations
make migrate-up

# Verify tables created
psql -U postgres -d centre_auth_service -c "\dt"

# Expected tables:
# - users
# - accounts
# - otp_verifications
# - device_sessions
# - refresh_tokens
# - farmers
# - suppliers
# etc.
```

**Notification-Service (if has migrations):**

```bash
cd noti-service

# Check for migration files
ls migrations/ 2>/dev/null || echo "No migrations directory"

# Run migrations if they exist
# (specific command depends on service setup)
```

---

## 🚀 Ready to Start Services

Once ALL checkboxes are complete:

- [ ] PostgreSQL installed and running on port 5432
- [ ] Redis installed and running on port 6379 (optional)
- [ ] Databases `centre_auth_service` and `notification_service` created
- [ ] All service configs use password "postgres"
- [ ] All service configs use correct database names
- [ ] Port configurations match between gateway and services
- [ ] Required ports (8080, 50051, 9012) are available
- [ ] Database migrations applied successfully
- [ ] Can connect to PostgreSQL: `psql -U postgres -d centre_auth_service`
- [ ] Can connect to Redis: `redis-cli ping` (if using Redis)

**If all checks pass, proceed to start services:**

```bash
# Terminal 1: Centre-Auth-Service
cd centre-auth-service
go run cmd/app/main.go

# Terminal 2: Notification-Service
cd noti-service
go run cmd/main.go

# Terminal 3: API Gateway
cd app-api-gateway
./bin/app api
# or
go run cmd/app/main.go api
```

---

## 🐛 Common Issues

### Issue: "password authentication failed"

**Cause**: PostgreSQL password mismatch

**Solution**:
```bash
# Reset PostgreSQL password
psql -U postgres
ALTER USER postgres WITH PASSWORD 'postgres';
\q
```

### Issue: "database does not exist"

**Cause**: Database not created

**Solution**: Run `scripts/setup-databases.sh` or create manually

### Issue: "connection refused" to PostgreSQL

**Cause**: PostgreSQL not running or wrong port

**Solution**: 
```bash
# Check service
pg_isready -h localhost -p 5432

# Start service
net start postgresql-x64-14  # Windows
```

### Issue: Port already in use

**Cause**: Another process using the port

**Solution**: Kill the process or use different port

---

## 📊 Quick Status Check Script

Save this as `check-status.sh`:

```bash
#!/bin/bash

echo "=== Infrastructure Status ==="
echo ""

# PostgreSQL
echo -n "PostgreSQL (5432): "
pg_isready -h localhost -p 5432 -U postgres &>/dev/null && echo "✅ Running" || echo "❌ Not running"

# Redis
echo -n "Redis (6379): "
redis-cli ping &>/dev/null && echo "✅ Running" || echo "❌ Not running"

# Databases
echo -n "Database centre_auth_service: "
psql -U postgres -lqt | cut -d \| -f 1 | grep -qw centre_auth_service && echo "✅ Exists" || echo "❌ Missing"

echo -n "Database notification_service: "
psql -U postgres -lqt | cut -d \| -f 1 | grep -qw notification_service && echo "✅ Exists" || echo "❌ Missing"

echo ""
echo "=== Service Ports ==="
netstat -ano | grep -E ":8080|:50051|:9012" | grep "LISTENING" || echo "No services running"

echo ""
```

Run with: `bash check-status.sh`

---

## 📝 Summary

This checklist ensures:
1. ✅ PostgreSQL and Redis are properly installed and running
2. ✅ Databases are created with correct names
3. ✅ All services use standardized configuration
4. ✅ Ports are available and not conflicting
5. ✅ Migrations are applied
6. ✅ Services can connect to infrastructure

Follow this checklist before every fresh setup or after system restart.
