# Docker Development Environment - Quick Start Guide

**Author:** Development Team  
**Created:** December 25, 2025  
**Last Updated:** December 25, 2025  
**Status:** Verified Working

---

## Overview

This guide provides step-by-step instructions to set up and test the AgriOS development environment using Docker. The environment includes:

- **CAS (Centre Auth Service)**: Authentication, suppliers, accounts management
- **Noti-Service**: FCM notification delivery
- **PostgreSQL**: Database for both services
- **Redis**: Cache and session storage

---

## Quick Start (5 minutes)

### Prerequisites

1. Docker Desktop running
2. grpcurl installed (`choco install grpcurl` or `brew install grpcurl`)
3. Go 1.21+ for building binaries
4. FCM credentials file (`noti-service/config/fcm-dev-sdk.json`)

### Step 1: Build Linux Binaries

**Windows PowerShell:**
```powershell
$env:CGO_ENABLED="0"; $env:GOOS="linux"; $env:GOARCH="amd64"

cd centre-auth-service
go build -o bin/cas-linux ./cmd/app/
cd ..

cd noti-service
go build -o bin/noti-linux ./cmd/main.go
cd ..
```

### Step 2: Start Docker

```bash
docker compose -f docker/docker-compose.dev.yml up -d --build
```

### Step 3: Apply Database Migrations

```bash
# Apply consolidated schema
cat centre-auth-service/migrations/final_schema.sql | docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth

# Apply additional migrations
for file in centre-auth-service/migrations/0{62,63,64,65,66,67,68,69,70}*.sql; do
  cat "$file" | docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth
done

# Fix missing column
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS name TEXT;"
```

### Step 4: Seed Test Data

```bash
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth << 'EOF'
-- Account with bcrypt hash for "password123"
INSERT INTO accounts (id, type, identifier, password_hash, source, is_supplier, is_active_supplier, code)
VALUES (999, 'phone', '0909999999', '$2y$10$Gjw4QnR8fJJN2YlKnAZVDOBY0kBiIiv7OxmCMqanEEc6JECVE3hp2', 'app', true, true, 'TEST001')
ON CONFLICT (id) DO UPDATE SET password_hash = EXCLUDED.password_hash;

-- Supplier
INSERT INTO suppliers (id, account_id, company_name, status)
VALUES (888, 999, 'Test Supplier Company', 'approved')
ON CONFLICT (id) DO NOTHING;

-- User profile
INSERT INTO users (id, account_id, name, phone)
VALUES (999, 999, 'Test Supplier User', '0909999999')
ON CONFLICT (id) DO NOTHING;

-- Device session (update with real FCM token later)
INSERT INTO device_sessions (id, account_id, device_id, firebase_token, is_active)
VALUES (1, 999, 'test-device-001', 'PLACEHOLDER', true)
ON CONFLICT (id) DO NOTHING;
EOF
```

### Step 5: Update FCM Token

Get real FCM token from mobile app and update:

```bash
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c \
  "UPDATE device_sessions SET firebase_token = 'YOUR_REAL_FCM_TOKEN' WHERE account_id = 999;"
```

---

## Testing the Full Flow

### Test 1: Login

```bash
grpcurl -plaintext -d '{"identifier": "0909999999", "password": "password123"}' \
  localhost:50051 auth.v1.AuthService/Login
```

Expected: `"code": "000"` with accessToken

### Test 2: DeactiveSupplier (requires auth token)

```bash
TOKEN="YOUR_ACCESS_TOKEN_FROM_LOGIN"
grpcurl -plaintext -H "authorization: Bearer $TOKEN" \
  -d '{"id": 888}' localhost:50051 supplier.v1.SupplierService/DeactiveSupplier
```

Expected: `"code": "000", "message": "Supplier status toggled successfully"`

### Test 3: Verify FCM Notification

```bash
# Check noti-service logs
docker logs agrios_dev_noti --tail 10

# Should see: "successfully sent fcm multicast. success: 1, failure: 0"
```

---

## Service Ports

| Service | Container | gRPC | HTTP |
|---------|-----------|------|------|
| PostgreSQL | agrios_dev_postgres | - | 5432 |
| Redis | agrios_dev_redis | - | 6379 |
| CAS | agrios_dev_cas | 50051 | 4000 |
| Noti-Service | agrios_dev_noti | 9012 | 8000 |

---

## Common Commands

```bash
# View all logs
docker compose -f docker/docker-compose.dev.yml logs -f

# View specific service logs
docker logs agrios_dev_cas --tail 50
docker logs agrios_dev_noti --tail 50

# Restart services
docker compose -f docker/docker-compose.dev.yml restart

# Stop all
docker compose -f docker/docker-compose.dev.yml down

# Full cleanup (remove data)
docker compose -f docker/docker-compose.dev.yml down -v
```

---

## Troubleshooting

### Login returns "Unauthorized"

Password hash mismatch. Update with correct bcrypt hash:

```bash
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c \
  "UPDATE accounts SET password_hash = '\$2y\$10\$Gjw4QnR8fJJN2YlKnAZVDOBY0kBiIiv7OxmCMqanEEc6JECVE3hp2' WHERE id = 999;"
```

### Login treated as SSO

Do NOT pass `provider` field for phone/email login:

```bash
# WRONG - treated as SSO
grpcurl -d '{"identifier": "0909999999", "password": "...", "provider": "phone"}' ...

# CORRECT - phone login
grpcurl -d '{"identifier": "0909999999", "password": "..."}' ...
```

### Column "name" does not exist

```bash
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c \
  "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS name TEXT;"
```

### FCM failure

- Ensure `noti-service/config/fcm-dev-sdk.json` exists
- Update device_sessions with real FCM token from mobile app

---

## Verified Test Results

| Date | Test Case | Result |
|------|-----------|--------|
| 2025-12-25 | Login API | PASS |
| 2025-12-25 | DeactiveSupplier | PASS |
| 2025-12-25 | CAS -> Noti gRPC | PASS |
| 2025-12-25 | FCM Multicast | PASS |
| 2025-12-25 | Mobile Notification | PASS |

---

## Related Documentation

- [Docker README](../docker/README.md) - Detailed Docker setup
- [TOB-37 Implementation](tob37/TOB37_IMPLEMENTATION.md) - FCM Event System
- [TOB-45 Implementation](tob45/TOB45_CAS_IMPLEMENTATION.md) - CAS Deactivation Flow
