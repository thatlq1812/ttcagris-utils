# TOB-45: CAS Service - Send Deactivate Supplier Event Implementation Guide

**Created:** December 25, 2025  
**Last Updated:** December 25, 2025  
**Status:** COMPLETED - Verified  
**Jira Ticket:** TOB-45 - [Training] Send deactive supplier event to app  
**Verified Date:** December 25, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Implementation Steps](#implementation-steps)
4. [Code Changes](#code-changes)
5. [Data Flow](#data-flow)
6. [Database Requirements and Seeding Data](#database-requirements-and-seeding-data)
7. [Testing Guide](#testing-guide)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Business Requirement

When an admin deactivates a supplier account in CAS (Centre Auth Service), the system should:
1. Toggle the supplier's `is_active_supplier` status
2. Send a notification event to the mobile app via FCM
3. Mobile app receives the event and performs force logout

### Technical Approach

- **Pattern**: Async notification using goroutine (non-blocking)
- **Flow**: CAS -> Noti-Service -> FCM -> Mobile App
- **Protocol**: gRPC for inter-service communication
- **FCM**: Data-only messages for event actions

### What Will Be Implemented

| Component | File | Description |
|-----------|------|-------------|
| SendEventToDevices method | `pkg/grpcclient/notification_client.go` | New gRPC client method to send FCM events |
| DeactiveSupplier enhancement | `internal/grpc/supplier_server.go` | Add async notification call after deactivation |
| Device lookup helper | `internal/grpc/supplier_server.go` | Get firebase tokens from supplier's account |

---

## Architecture

### Service Flow

```
┌─────────────────┐                ┌──────────────────┐                ┌─────────────┐
│   Admin Panel   │                │   CAS Service    │                │ Noti-Service│
│                 │────[Toggle]───>│   (port 50051)   │────[gRPC]─────>│ (port 9012) │
└─────────────────┘                └──────────────────┘                └──────────────┘
                                          │                                   │
                                          │ 1. DeactiveSupplier()             │
                                          │ 2. Get Supplier AccountID         │
                                          │ 3. Get DeviceSessions             │
                                          │ 4. Extract Firebase Tokens        │
                                          │                                   v
                                          │                            ┌──────────────┐
                                          │                            │   Firebase   │
                                          │                            │     FCM      │
                                          │                            └──────┬───────┘
                                          │                                   │
                                          v                                   v
                                   ┌──────────────┐                    ┌─────────────┐
                                   │   Response   │                    │ Mobile App  │
                                   │  to Admin    │                    │ (Logout)    │
                                   └──────────────┘                    └─────────────┘
```

### Service Ports

| Service | gRPC Port | HTTP Port |
|---------|-----------|-----------|
| CAS | 50051 | 4000 |
| Noti-service | 9012 | 8000 |

---

## Implementation Steps

### Step 1: Add SendEventToDevices Method to NotificationClient

Add a new method in `pkg/grpcclient/notification_client.go` to call `SendEventToDevices` RPC of noti-service.

**Location:** `centre-auth-service/pkg/grpcclient/notification_client.go`

**Important Note:** Since `SendEventToDevices` is defined in noti-service's local `api.v1` proto (not in Core proto), we use a local proto type (`sendEventToDevicesRequest`) defined in [noti_api_types.go](centre-auth-service/pkg/grpcclient/noti_api_types.go) that mirrors the noti-service proto structure.

### Step 2: Update SupplierServer to Include Dependencies

Update `internal/grpc/supplier_server.go` to include notification client and device usecase.

**Current Structure:**
```go
type SupplierServer struct {
    pb.UnimplementedSupplierServiceServer
    supplierUsecase usecase.SupplierUsecase
    storageClient   *storage.Client
    logger          *zap.Logger
}
```

**Updated Structure:**
```go
type SupplierServer struct {
    pb.UnimplementedSupplierServiceServer
    supplierUsecase    usecase.SupplierUsecase
    deviceUsecase      usecase.DeviceUsecase
    notificationClient *grpcclient.NotificationClient
    storageClient      *storage.Client
    logger             *zap.Logger
}
```

### Step 3: Update Constructor

```go
func NewSupplierServer(
    supplierUsecase usecase.SupplierUsecase,
    deviceUsecase usecase.DeviceUsecase,
    notificationClient *grpcclient.NotificationClient,
    storageClient *storage.Client,
    logger *zap.Logger,
) *SupplierServer {
    return &SupplierServer{
        supplierUsecase:    supplierUsecase,
        deviceUsecase:      deviceUsecase,
        notificationClient: notificationClient,
        storageClient:      storageClient,
        logger:             logger,
    }
}
```

### Step 4: Update DeactiveSupplier Method

**Location:** `centre-auth-service/internal/grpc/supplier_server.go`

### Step 5: Add Required Import

Add the `time` package import in `supplier_server.go`:

### Step 6: Update Server Registration

Update the server registration in bootstrap/container where SupplierServer is created to pass the new dependencies.

---

## Data Flow

### Firebase Token Lookup Flow

```
1. DeactiveSupplier(supplier_id: 123)
   |
   v
2. Get Supplier by ID
   -> supplier.AccountID = 456
   |
   v
3. GetActiveDevicesByAccountID(account_id: 456)
   -> Returns: [
        { device_id: "abc", firebase_token: "fcm_token_1" },
        { device_id: "xyz", firebase_token: "fcm_token_2" }
      ]
   |
   v
4. Extract firebase_tokens: ["fcm_token_1", "fcm_token_2"]
   |
   v
5. SendEventToDevices(tokens, action_code="001", model="suppliers", action="deactivate")
   |
   v
6. Noti-service sends FCM data message to tokens
   |
   v
7. Mobile app receives event and triggers force logout
```

### FCM Payload Sent to Mobile App

```json
{
  "action_code": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Your supplier account has been deactivated. Please contact support for more information."
}
```

---

## Database Requirements and Seeding Data

### Required Tables

The notification flow depends on data in the following tables:

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `suppliers` | Supplier profiles | `id`, `account_id`, `is_active_supplier` |
| `accounts` | User accounts | `id`, `phone`, `is_supplier` |
| `device_sessions` | Device registration | `account_id`, `device_id`, `firebase_token`, `is_active` |

### Data Dependency Chain

```
suppliers.id (123)
    |
    +-- suppliers.account_id (456)
            |
            +-- device_sessions.account_id (456)
                    |
                    +-- device_sessions.firebase_token ("eAVmjf6OTJ6mo...")
```

**Important:** If any link in this chain is missing, the notification will not be sent.

### Verify Data Before Testing

Before testing, ensure the database has complete data:

```sql
-- 1. Check supplier exists and has account_id
SELECT id, account_id, is_active_supplier 
FROM suppliers 
WHERE id = YOUR_SUPPLIER_ID;

-- 2. Check account exists
SELECT id, phone, is_supplier 
FROM accounts 
WHERE id = YOUR_ACCOUNT_ID;

-- 3. Check device session has firebase_token
SELECT id, account_id, device_id, firebase_token, is_active 
FROM device_sessions 
WHERE account_id = YOUR_ACCOUNT_ID AND is_active = true;
```

### Seeding Data for Testing

If database is empty, insert test data:

```sql
-- 1. Create test account (if not exists)
INSERT INTO accounts (id, phone, password_hash, is_supplier, is_active_supplier, created_at, updated_at)
VALUES (456, '0901234567', '$2a$10$...', true, true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 2. Create test supplier (if not exists)
INSERT INTO suppliers (id, account_id, company_name, status, is_active_supplier, created_at, updated_at)
VALUES (123, 456, 'Test Supplier Co.', 'approved', true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- 3. Create device session with FCM token
-- NOTE: Replace firebase_token with REAL token from mobile app
INSERT INTO device_sessions (account_id, device_id, firebase_token, device_type, is_active, created_at, updated_at)
VALUES (
    456,
    'test-device-001',
    'YOUR_REAL_FCM_TOKEN_FROM_MOBILE_APP',  -- Get this from mobile app
    'android',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (account_id, device_id) 
DO UPDATE SET firebase_token = EXCLUDED.firebase_token, updated_at = NOW();
```

### Getting Real FCM Token

The `firebase_token` must be a real token from the mobile app:

1. Install demo mobile app on physical device
2. Open app and go to login/home screen
3. Tap "Copy Token" button
4. Use the copied token in the seed data above

**Note:** FCM tokens from Android Emulator may not work reliably. Use a physical device for testing.

---

## Build and Development Workflow

Follow this standard workflow before testing APIs.

### Step 1: Prepare Dependencies

```bash
cd centre-auth-service

# Update go.mod and remove unused dependencies
go mod tidy

# Vendor all dependencies (for reproducible builds)
go mod vendor
```

### Step 2: Build Binary

```bash
# Build using Makefile
make build

# Or manual build
go build -o bin/app ./cmd/app/
```

### Step 3: Generate Code (if proto changes)

```bash
# Only needed if you modified proto files
make generate
```

### Step 4: Build Docker (Optional)

```bash
# Build Docker image
docker build -t cas-service:latest .

# Run Docker container
docker run -p 50051:50051 -p 4000:4000 \
  -e DATABASE_URL="postgres://..." \
  cas-service:latest
```

### Step 5: Verify Build

```bash
# Check binary was created
ls -la bin/app

# Check version/health
./bin/app --version
```

### Quick Commands Summary

| Command | Description |
|---------|-------------|
| `go mod tidy` | Clean up go.mod |
| `go mod vendor` | Vendor dependencies |
| `make build` | Build binary |
| `make generate` | Generate proto code |
| `make api` | Run service locally |
| `make test` | Run unit tests |
| `make lint` | Run linter |

---

## Testing Guide

### Authentication Flow

**Important:** `DeactiveSupplier` requires authentication (Bearer token).

| Scenario | Result |
|----------|--------|
| No token | `Unauthenticated: missing authorization token` |
| Valid token | Success |
| Invalid/expired token | `Unauthenticated: invalid token` |

**Security Architecture:**

```
┌─────────────┐      REST + Token     ┌──────────────┐      gRPC        ┌─────────────┐
│  Admin Web  │ ───────────────────── │ API Gateway  │ ─────────────────│    CAS      │
│  (Browser)  │                       │  (port 8080) │                  │ (port 50051)│
└─────────────┘                       └──────────────┘                  └─────────────┘
                                             │
                                      Check role/permission
                                      (before forwarding)
```

- **Production:** Gateway checks admin role before forwarding to CAS
- **Dev/Test:** Direct gRPC call to CAS only needs valid token (bypasses role check)
- **Port 50051:** Not exposed to internet, internal network only

### Prerequisites

1. Docker Desktop running
2. grpcurl installed
3. FCM credentials at `noti-service/config/fcm-dev-sdk.json`
4. Real FCM token from mobile app

### Docker Quick Start (Full Procedure)

Complete procedure to start Docker dev environment from scratch.

**Step 1: Build Linux Binaries**

```bash
# Windows (Git Bash/WSL)
cd centre-auth-service && mkdir -p bin && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o bin/cas-linux ./cmd/app/
cd ../noti-service && mkdir -p bin && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o bin/noti-linux ./cmd/main.go
cd ..

# Verify binaries are Linux ELF
file centre-auth-service/bin/cas-linux  # Should show: ELF 64-bit LSB executable
file noti-service/bin/noti-linux        # Should show: ELF 64-bit LSB executable
```

**Step 2: Ensure FCM Credentials**

```bash
# FCM credentials must be at noti-service/config/fcm-dev-sdk.json
ls -la noti-service/config/fcm*.json
```

**Step 3: Start Docker Containers**

```bash
docker compose -f docker/docker-compose.dev.yml up -d --build

# Wait for containers to be ready
sleep 10 && docker compose -f docker/docker-compose.dev.yml ps
```

**Step 4: Reset and Migrate Database**

```bash
# Stop services to release database connections
docker stop agrios_dev_cas agrios_dev_noti

# Reset database
docker exec -i agrios_dev_postgres psql -U postgres << 'EOF'
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'centre_auth' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS centre_auth;
CREATE DATABASE centre_auth;
GRANT ALL PRIVILEGES ON DATABASE centre_auth TO postgres;
EOF

# Apply migrations
cat centre-auth-service/migrations/final_schema.sql | docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth

# Apply additional migrations (062+)
for f in centre-auth-service/migrations/06[2-9]*.sql centre-auth-service/migrations/07*.sql; do
  [ -f "$f" ] && cat "$f" | docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth 2>&1 | grep -E "ERROR" || true
done

# Add missing column (if needed)
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS name TEXT;"
```

**Step 5: Seed Test Data**

```bash
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth << 'EOSEED'
BEGIN;

-- Account with password "password123" (bcrypt hash)
INSERT INTO accounts (id, type, identifier, password_hash, source, is_supplier, is_active_supplier, code, created_at, updated_at)
VALUES (999, 'phone', '0909999999', '$2y$10$Gjw4QnR8fJJN2YlKnAZVDOBY0kBiIiv7OxmCMqanEEc6JECVE3hp2', 'app', true, true, 'TEST001', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET password_hash = EXCLUDED.password_hash, is_active_supplier = true, updated_at = NOW();

-- User profile
INSERT INTO users (id, name, phone, account_id, created_at, updated_at)
VALUES (999, 'Test Supplier User', '0909999999', 999, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET account_id = 999, updated_at = NOW();

-- Supplier
INSERT INTO suppliers (id, account_id, company_name, status, name, is_deleted, created_at, updated_at)
VALUES (888, 999, 'Test Supplier Company', 'approved', 'Test Supplier', false, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET account_id = 999, status = 'approved', updated_at = NOW();

-- Device session with real FCM token (replace with your token)
INSERT INTO device_sessions (id, account_id, device_id, firebase_token, device_type, device_name, is_active, created_at, updated_at)
VALUES (1, 999, 'test-device-001', 'cwv6o7R3THiaLdRcpeEp_D:APA91bFXHco-bF1IK8Ft8HxEn0ibGwUfz-LEA2uE5WBhF4MExzDD68n6dA16MpfHf0p0S4Re3M2PiyS-Or4NwjexTaT_SAnBQQ9neHH4y6cQo4z3zrhqX-k', 'android', 'Test Device', true, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET firebase_token = EXCLUDED.firebase_token, is_active = true, updated_at = NOW();

COMMIT;

-- Verify
SELECT id, identifier, is_supplier, is_active_supplier FROM accounts WHERE id = 999;
SELECT id, account_id, company_name, status FROM suppliers WHERE id = 888;
SELECT id, account_id, LEFT(firebase_token, 40) as token_preview, is_active FROM device_sessions WHERE account_id = 999;
EOSEED
```

**Step 6: Start Services**

```bash
docker start agrios_dev_cas agrios_dev_noti
sleep 10 && docker compose -f docker/docker-compose.dev.yml ps
```

**Step 7: Verify Services**

```bash
# Check gRPC endpoints
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:9012 list api.v1.NotificationService
```

### Update FCM Token

Get real FCM token from mobile app and update:

```bash
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c \
  "UPDATE device_sessions SET firebase_token = 'YOUR_REAL_FCM_TOKEN' WHERE account_id = 999;"
```

### Test Flow

#### Step 1: Login to Get Token

```bash
grpcurl -plaintext -d '{"identifier": "0909999999", "password": "password123"}' \
  localhost:50051 auth.v1.AuthService/Login
```

**Note:** Do NOT include `provider` field - it will be treated as SSO login.

Save the `accessToken` from response.

#### Step 2: Test Without Token (Should Fail)

```bash
grpcurl -plaintext -d '{"id": 888}' localhost:50051 supplier.v1.SupplierService/DeactiveSupplier
```

Expected:
```
ERROR: Unauthenticated: missing authorization token
```

#### Step 3: Test With Token (Should Succeed)

```bash
TOKEN="YOUR_ACCESS_TOKEN_FROM_STEP_1"
grpcurl -plaintext -H "authorization: Bearer $TOKEN" \
  -d '{"id": 888}' localhost:50051 supplier.v1.SupplierService/DeactiveSupplier
```

Expected:
```json
{
  "code": "000",
  "message": "Supplier status toggled successfully",
  "data": {
    "isActiveSupplier": false
  }
}
```

#### Step 4: Verify FCM Notification

```bash
# Check noti-service logs
docker logs agrios_dev_noti --tail 10

# Should see: "successfully sent fcm multicast. success: 1, failure: 0"
```

#### Step 5: Toggle Back (Re-activate)

Call same API again - FCM only sent when deactivating (false), not activating (true).

### Verified Test Results (2025-12-25)

| Test Case | Result | Details |
|-----------|--------|---------|
| Login API | PASS | Account 999 (phone: 0909999999), password: password123 |
| Call without token | PASS | Rejected with `Unauthenticated` |
| Call with token | PASS | Supplier 888 status toggled to `is_active_supplier: false` |
| CAS -> Noti gRPC | PASS | SendEventToDevices called with action_code=001 |
| FCM Multicast | PASS | success: 1, failure: 0 |
| Mobile Notification | PASS | Push notification received on physical device |

**CAS Logs (Success):**
```
{"msg":"DeactiveSupplier success","supplier_id":888,"is_active_supplier":false}
{"msg":"sending event to devices","device_count":1,"action_code":"001","model":"suppliers","action":"deactivate"}
{"msg":"event sent to devices","success_count":1,"failure_count":0}
{"msg":"deactivate notification sent successfully","supplier_id":888,"account_id":999,"success_count":1,"failure_count":0}
```

**Noti-Service Logs (Success):**
```
{"msg":"successfully sent fcm multicast. success: 1, failure: 0"}
{"msg":"finished unary call with code OK","grpc.service":"api.v1.NotificationService","grpc.method":"SendEventToDevices"}
```

**Test Environment:**
- Docker containers: postgres:17-alpine, redis:7-alpine, cas-service, noti-service
- Ports: CAS (50051/4000), Noti (9012/8000), PostgreSQL (5432), Redis (6379)
- FCM Token: Real token from mobile app (verified working)
- Test Account: 999 (phone: 0909999999, password: password123)
- Test Supplier: 888 (Test Supplier Company)

### Direct Noti-Service Test (Bypass CAS)

```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN"],
  "actionCode": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Direct test"
}' localhost:9012 api.v1.NotificationService/SendEventToDevices
```

---

## Non-Docker Testing (Local Go)

If you prefer running services locally without Docker:

**Terminal 1 - Noti-Service:**
```bash
cd noti-service
go run cmd/main.go
```

**Terminal 2 - CAS Service:**
```bash
cd centre-auth-service
go run cmd/app/main.go api
```

**Terminal 3 - Test:**
```bash
# Login first
grpcurl -plaintext -d '{"identifier": "0909999999", "password": "password123"}' \
  localhost:50051 auth.v1.AuthService/Login

# Then call with token
TOKEN="..."
grpcurl -plaintext -H "authorization: Bearer $TOKEN" \
  -d '{"id": 888}' localhost:50051 supplier.v1.SupplierService/DeactiveSupplier
```

---

## Gateway REST API (Production)

In production, admin web calls via API Gateway:

```bash
curl -X POST http://localhost:8080/api/v1/suppliers/888/deactivate \
  -H "Authorization: Bearer <ADMIN_TOKEN>" \
  -H "Content-Type: application/json"
```

Gateway will:
1. Validate admin token
2. Check admin has `supplier:deactivate` permission
3. Forward to CAS gRPC

------

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Notification not sent | No firebase token | Check device_sessions table has firebase_token |
| FCM token invalid | Token expired | Re-login on mobile app to refresh token |
| Goroutine not executing | Context cancelled | Use `context.Background()` for async operations |
| Connection refused | Service not running | Verify noti-service is running on port 9012 |

### Debug Checklist

1. **Check device has firebase token:**
```sql
SELECT firebase_token, device_id, is_active
FROM device_sessions
WHERE account_id = 456;
```

2. **Check supplier has account_id:**
```sql
SELECT id, account_id, is_active_supplier
FROM suppliers
WHERE id = 123;
```

3. **Verify noti-service connectivity:**
```bash
grpcurl -plaintext localhost:9012 list api.v1.NotificationService
```

4. **Test SendEventToDevices directly:**
```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN"],
  "actionCode": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Test force logout"
}' localhost:9012 api.v1.NotificationService/SendEventToDevices
```

---

## Action Code Registry

### Force Logout Events (001-010)

| Code | Model | Action | Description |
|------|-------|--------|-------------|
| 001 | suppliers | deactivate | Supplier deactivated - Force logout |
| 002 | buyers | deactivate | Buyer deactivated - Force logout |
| 003 | suppliers | suspend | Supplier suspended - Force logout |
| 004 | buyers | suspend | Buyer suspended - Force logout |

---

## Related Files

| File | Description |
|------|-------------|
| `centre-auth-service/pkg/grpcclient/notification_client.go` | Notification gRPC client |
| `centre-auth-service/internal/grpc/supplier_server.go` | Supplier gRPC server |
| `centre-auth-service/internal/usecase/device_usecase.go` | Device session usecase |
| `noti-service/internal/service/notification_grpc_service.go` | Noti-service handler |
| `docs/tob37/TOB37_IMPLEMENTATION.md` | FCM event system documentation |

---

## Implementation Status

### Completed Changes

| File | Change |
|------|--------|
| `pkg/grpcclient/notification_client.go` | Added `SendEventToDevices` method |
| `internal/grpc/supplier_server.go` | Updated struct, constructor, added `sendDeactivateNotification` |
| `internal/grpc/server.go` | Updated `NewServer` to accept `notificationClient` |
| `internal/api/init.go` | Added `NotificationClient` to `Layers` struct |
| `internal/api/run.go` | Pass `NotificationClient` to `NewServer` |

### Verified Test Results (2025-12-25)

| Test Case | Result | Details |
|-----------|--------|---------|  
| Login API | PASS | Account 999, password: password123 |
| DeactiveSupplier | PASS | Supplier 888 status toggled |
| CAS -> Noti-service gRPC | PASS | SendEventToDevices called with action_code=001 |
| FCM Multicast | PASS | success: 1, failure: 0 |
| Mobile App Notification | PASS | Push notification received on device |

**Test Environment:**
- Docker containers: postgres, redis, cas-service, noti-service
- FCM Token: Real token from mobile app
- Account: 999 (phone: 0909999999)
- Supplier: 888 (Test Supplier Company)

### Remaining Tasks

1. Add unit tests for `sendDeactivateNotification` method
2. Add integration tests in CI/CD pipeline
3. Production deployment checklist
