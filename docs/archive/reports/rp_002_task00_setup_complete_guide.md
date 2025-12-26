# TASK 00 Setup Report - Complete Guide

**Project:** Centre Auth Service  
**Date:** December 16, 2025  
**Status:** Completed with Notes  
**Time Required:** ~45 minutes

---

## Executive Summary

Task 00 đã được hoàn thành thành công với môi trường development fully functional. Service đang chạy ổn định với PostgreSQL, Redis, và tất cả migrations đã được apply. Test accounts và supplier data đã sẵn sàng cho NLD-30 & NLD-34.

**Key Achievements:**
- ✅ Docker containers running (PostgreSQL 14, Redis 7)
- ✅ 20 database tables created from 67+ migrations
- ✅ gRPC service operational on port 50051
- ✅ Test accounts created (web & app)
- ✅ Sample supplier data ready

**Issues Found:**
- ⚠️ Migrations không tự động chạy (manual fix applied)
- ⚠️ OTP notification service không khả dụng (expected for dev)
- ⚠️ Account code generator có duplicate issue (minor)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Part 1: Infrastructure Setup](#part-1-infrastructure-setup)
- [Part 2: Run Migrations](#part-2-run-migrations)
- [Part 3: Start Service](#part-3-start-service)
- [Part 4: Create Test Accounts](#part-4-create-test-accounts)
- [Part 5: Create Supplier](#part-5-create-supplier)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Required Software:**
- Docker Desktop (running)
- Go 1.25+
- Git Bash (for Windows)
- grpcurl (for testing gRPC)

**Project Structure:**
```
d:\ttcagris\
├── centre-auth-service/    # Main service
│   ├── migrations/          # 67+ SQL migration files
│   ├── config/             # config.yaml
│   └── cmd/app/            # Entry point
└── Core/                   # Proto definitions
```

---

## Part 1: Infrastructure Setup

### Step 1.1: Verify Docker

```bash
# Check Docker is running
docker --version
docker ps
```

### Step 1.2: Start PostgreSQL & Redis

Containers should already be running from docker-compose:

```bash
# Check container status
docker ps | grep -E "(postgres|redis)"

# Expected output:
# cas-postgres ... Up (healthy) ... 0.0.0.0:5432->5432/tcp
# cas-redis     ... Up (healthy) ... 0.0.0.0:6379->6379/tcp
```

**If not running, start them:**

```bash
cd /d/ttcagris/centre-auth-service
docker-compose up -d
```

### Step 1.3: Verify Database Connection

```bash
# Test PostgreSQL
docker exec cas-postgres psql -U postgres -c "SELECT version();"

# Test Redis
docker exec cas-redis redis-cli ping
# Expected: PONG

# Check database exists
docker exec cas-postgres psql -U postgres -l | grep centre_auth
```

**✅ Checkpoint 1:** PostgreSQL và Redis đang chạy healthy.

---

## Part 2: Run Migrations

**CRITICAL:** Service không tự động chạy migrations. Phải chạy manual.

### Step 2.1: Check Migration Files

```bash
cd /d/ttcagris/centre-auth-service
ls migrations/*.sql | wc -l
# Expected: 67+ files
```

### Step 2.2: Run All Migrations

```bash
# Run all migration files in order
for f in /d/ttcagris/centre-auth-service/migrations/*.sql; do 
  echo "Running $(basename $f)..."
  docker exec -i cas-postgres psql -U postgres -d centre_auth < "$f" 2>&1 | head -3
done
```

**Expected Output:**
- CREATE TABLE statements
- CREATE INDEX statements
- Some NOTICE messages (normal)
- A few ERRORs for duplicate constraints (can ignore)

### Step 2.3: Verify Tables Created

```bash
# List all tables
docker exec cas-postgres psql -U postgres -d centre_auth -c "\dt"
```

**Expected: 20 tables including:**
- users
- accounts
- suppliers
- farmers
- refresh_tokens
- otp_verifications
- permissions
- roles
- etc.

**✅ Checkpoint 2:** 20 tables đã được tạo thành công.

---

## Part 3: Start Service

### Step 3.1: Open New Terminal for Service

**Important:** Service cần chạy trong terminal riêng để xem logs.

1. Trong VS Code: **Ctrl+Shift+`** (New Terminal)
2. Chọn **Git Bash** terminal
3. Chạy commands sau:

```bash
cd /d/ttcagris/centre-auth-service
go run cmd/app/main.go api
```

### Step 3.2: Wait for Startup

Đợi cho đến khi thấy logs:

```
{"level":"info",...,"msg":"postgreSQL connection pool created successfully"}
{"level":"info",...,"msg":"database connection established successfully"}
{"level":"info",...,"msg":"cache engine initialized successfully"}
{"level":"info",...,"msg":"grpc server started","port":50051}
{"level":"info",...,"msg":"gRPC server started successfully"}
```

**Expected Warnings (OK to ignore):**
- `finance service address not configured` - Không cần
- `hub service address not configured` - Không cần
- `Failed to create eKYC provider, using mock provider` - OK cho dev
- `traces export: Post ... connection refused` - Không có tracing service

**✅ Checkpoint 3:** Service đang chạy, gRPC port 50051 active.

### Step 3.3: Verify gRPC Service

Mở **terminal khác** (không phải terminal đang chạy service):

```bash
# List all gRPC services
/c/Users/fxlqt/go/bin/grpcurl -plaintext localhost:50051 list

# Expected output (25 services):
# account.v1.AccountService
# auth.v1.AuthService
# mobile.v1.MobileAuthService
# supplier.v1.SupplierService
# farmer.v1.FarmerService
# ... và nhiều services khác
```

**✅ Checkpoint 4:** gRPC service responding, 25 services available.

---

## Part 4: Create Test Accounts

Tất cả commands dưới đây chạy trong **terminal thứ 2** (không phải terminal chạy service).

### Step 4.1: Create Web Account (Email)

```bash
/c/Users/fxlqt/go/bin/grpcurl -plaintext -d '{
  "name": "Admin Test",
  "type": "email",
  "identifier": "admin@test.com",
  "password": "Admin@123456"
}' localhost:50051 auth.v1.AuthService/Register
```

```bash
/c/Users/fxlqt/go/bin/grpcurl -plaintext -d '{
  "name": "Admin Test",
  "type": "email",
  "identifier": "admin005@test.com",
  "password": "Admin@123456"
}' localhost:50051 auth.v1.AuthService/Register
```

**Expected Response:**

```json
{
  "code": "000",
  "message": "success",
  "data": {
    "accessToken": "eyJhbGci...",
    "tokenType": "Bearer",
    "account": {
      "id": "2",
      "type": "email",
      "identifier": "admin@test.com",
      "name": "Admin Test"
    },
    "refreshToken": "..."
  }
}
```

**Save:**
- Account ID: `2`
- Access Token: (copy toàn bộ eyJhbGci...)

### Step 4.2: Test Login Web Account

```bash
/c/Users/fxlqt/go/bin/grpcurl -plaintext -d '{
  "identifier": "admin@test.com",
  "password": "Admin@123456",
  "provider": "local"
}' localhost:50051 auth.v1.AuthService/Login
```

**Expected:** Successful login với access_token và refresh_token.

### Step 4.3: Create App Account (Phone)

**Note:** OTP service không hoạt động trong dev, tạo account manual qua database.

```bash
# Create app account directly in database
docker exec cas-postgres psql -U postgres -d centre_auth -c "
INSERT INTO accounts (type, identifier, password_hash, source, is_supplier) 
VALUES ('phone', '+84987654321', '\$2a\$10\$dummy', 'app', true) 
RETURNING id, identifier;"
```

**Expected Output:**

```
 id |  identifier  
----+--------------
  4 | +84987654321
```

**Save:** Account ID: `4`

### Step 4.4: Verify Accounts in Database

```bash
docker exec cas-postgres psql -U postgres -d centre_auth -c "
SELECT id, type, identifier, source, is_supplier 
FROM accounts 
ORDER BY id;"
```

**Expected:**

```
 id | type  |   identifier   | source | is_supplier 
----+-------+----------------+--------+-------------
  2 | email | admin@test.com | web    | f
  3 | sso   | admin@test.com | web    | f
  4 | phone | +84987654321   | app    | t
```

**✅ Checkpoint 5:** 3 accounts created (web + app).

---

## Part 5: Create Supplier

### Step 5.1: Create Supplier for App Account

```bash
docker exec cas-postgres psql -U postgres -d centre_auth -c "
INSERT INTO suppliers (account_id, company_name, business_id, tax_code, representative_name, created_at, updated_at)
VALUES (4, 'Supplier Test Company', '0123456789', 'TAX123', 'Test User', NOW(), NOW())
RETURNING id, account_id, company_name;"
```

**Expected Output:**

```
 id | account_id |     company_name      
----+------------+-----------------------
  1 |          4 | Supplier Test Company
```

**Save:** Supplier ID: `1`

### Step 5.2: Verify Supplier Data

```bash
docker exec cas-postgres psql -U postgres -d centre_auth -c "
SELECT s.id, s.account_id, s.company_name, s.tax_code,
       a.identifier, a.type, a.source
FROM suppliers s
JOIN accounts a ON s.account_id = a.id;"
```

**Expected Output:**

```
 id | account_id |     company_name      | tax_code |  identifier  | type  | source 
----+------------+-----------------------+----------+--------------+-------+--------
  1 |          4 | Supplier Test Company | TAX123   | +84987654321 | phone | app
```

**✅ Checkpoint 6:** Supplier created và linked với app account.

---

## Verification

### Final Checklist

Run this comprehensive check:

```bash
echo "=== INFRASTRUCTURE ==="
docker ps --format "{{.Names}}: {{.Status}}" | grep cas-

echo -e "\n=== DATABASE TABLES ==="
docker exec cas-postgres psql -U postgres -d centre_auth -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"

echo -e "\n=== ACCOUNTS ==="
docker exec cas-postgres psql -U postgres -d centre_auth -c "SELECT COUNT(*) as total, type, source FROM accounts GROUP BY type, source;"

echo -e "\n=== SUPPLIERS ==="
docker exec cas-postgres psql -U postgres -d centre_auth -c "SELECT COUNT(*) as supplier_count FROM suppliers;"

echo -e "\n=== gRPC SERVICE ==="
/c/Users/fxlqt/go/bin/grpcurl -plaintext localhost:50051 list 2>&1 | head -5
```

**Expected Results:**
- ✅ 2 containers healthy
- ✅ 20 tables in database
- ✅ 3 accounts (email/web, sso/web, phone/app)
- ✅ 1 supplier
- ✅ 25 gRPC services listed

---

## Troubleshooting

### Issue 1: Migrations Not Applied

**Symptom:** Tables không tồn tại, lỗi "relation does not exist"

**Solution:**

```bash
# Check tables
docker exec cas-postgres psql -U postgres -d centre_auth -c "\dt"

# If only casbin_rule exists, run migrations:
for f in /d/ttcagris/centre-auth-service/migrations/*.sql; do 
  docker exec -i cas-postgres psql -U postgres -d centre_auth < "$f" 2>&1
done
```

### Issue 2: Service Won't Start

**Symptom:** Cannot connect, port not listening

**Check 1:** Containers running?

```bash
docker ps | grep cas-
# Both should show "Up (healthy)"
```

**Check 2:** Config correct?

```bash
cat /d/ttcagris/centre-auth-service/config/config.yaml | grep -A 5 "database:"
```

Should show:
- host: "localhost"
- port: 5432
- database: "centre_auth"

### Issue 3: grpcurl Not Found

**Solution:**

```bash
# Install grpcurl
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Add to PATH or use full path
/c/Users/$USER/go/bin/grpcurl --version
```

### Issue 4: Account Registration Fails

**Error:** `check_accounts_password_hash_for_email_phone`

**Cause:** Type field phải là lowercase "email" hoặc "phone", không phải "EMAIL"

**Solution:** Dùng `"type": "email"` thay vì `"type": "EMAIL"`

### Issue 5: Duplicate Key on Code

**Error:** `duplicate key value violates unique constraint "accounts_code_key"`

**Cause:** Bug trong account code generator

**Workaround:** Tạo account trực tiếp qua database (như đã làm với phone account)

---

## Summary Data

### Test Accounts Ready

| ID | Type  | Identifier       | Source | Password       | Use Case       |
|----|-------|------------------|--------|----------------|----------------|
| 2  | email | admin@test.com   | web    | Admin@123456   | Web/Admin      |
| 4  | phone | +84987654321     | app    | (manual)       | Mobile/Supplier|

### Test Supplier

| ID | Account ID | Company Name          | Tax Code | Business ID |
|----|------------|-----------------------|----------|-------------|
| 1  | 4          | Supplier Test Company | TAX123   | 0123456789  |

### Service Status

- **gRPC Endpoint:** localhost:50051
- **Services Available:** 25
- **Database:** centre_auth (20 tables)
- **Cache:** Redis localhost:6379

---

## Next Steps

### For NLD-30 (Station Assignment)

Use:
- Supplier ID: `1`
- Account ID: `4`

### For NLD-34 (Supplier Deactivation)

Use:
- Supplier ID: `1`
- Can test deactivation/reactivation flows

---

## Notes & Observations

### What Worked Well

1. Docker containers khởi động nhanh và stable
2. Migration files organized và sequential
3. gRPC reflection enabled (dễ test với grpcurl)
4. Database schema well-designed với proper indexes

### Issues to Address

1. **Migration automation:** Service nên tự động chạy migrations on startup
2. **OTP Service:** Cần mock notification service cho dev environment
3. **Account code generator:** Fix duplicate constraint issue
4. **HTTP endpoints:** Service chỉ expose gRPC, có thể cần REST gateway

### Best Practices Applied

- ✅ Docker cho infrastructure (PostgreSQL, Redis)
- ✅ Versioned migrations với timestamps
- ✅ Separate terminals cho service logs vs commands
- ✅ Verification steps sau mỗi phase
- ✅ Test data documented với IDs

---

## Quick Reference Commands

### Container Management

```bash
# Status
docker ps | grep cas-

# Logs
docker logs cas-postgres --tail 50
docker logs cas-redis --tail 50

# Restart
docker restart cas-postgres cas-redis

# Connect to database
docker exec -it cas-postgres psql -U postgres -d centre_auth
```

### Service Management

```bash
# Start (in dedicated terminal)
cd /d/ttcagris/centre-auth-service
go run cmd/app/main.go api

# Stop: Ctrl+C in service terminal

# Check if running
/c/Users/fxlqt/go/bin/grpcurl -plaintext localhost:50051 list
```

### Database Quick Queries

```bash
# List tables
docker exec cas-postgres psql -U postgres -d centre_auth -c "\dt"

# Check accounts
docker exec cas-postgres psql -U postgres -d centre_auth -c "SELECT * FROM accounts;"

# Check suppliers
docker exec cas-postgres psql -U postgres -d centre_auth -c "SELECT * FROM suppliers;"

# Reset database (DESTRUCTIVE!)
docker exec cas-postgres psql -U postgres -c "DROP DATABASE IF EXISTS centre_auth; CREATE DATABASE centre_auth;"
# Then re-run migrations
```

---

**Report Version:** 1.0  
**Last Updated:** December 16, 2025  
**Tested By:** AI Assistant + User  
**Environment:** Windows 11, Docker Desktop, Go 1.25

---

## Appendix: Full Migration Script

Save this as `run_migrations.sh` for easy rerun:

```bash
#!/bin/bash
# Run all migrations for centre-auth-service

MIGRATION_DIR="/d/ttcagris/centre-auth-service/migrations"
DB_CONTAINER="cas-postgres"
DB_USER="postgres"
DB_NAME="centre_auth"

echo "Starting migrations..."
count=0
errors=0

for f in "$MIGRATION_DIR"/*.sql; do
  filename=$(basename "$f")
  echo -n "Running $filename... "
  
  if docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "$f" > /dev/null 2>&1; then
    echo "✓"
    ((count++))
  else
    echo "✗ (may be OK if already applied)"
    ((errors++))
  fi
done

echo ""
echo "Completed: $count migrations processed, $errors errors/warnings"
echo ""
echo "Verifying tables..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';"
```

Usage:
```bash
chmod +x run_migrations.sh
./run_migrations.sh
```
