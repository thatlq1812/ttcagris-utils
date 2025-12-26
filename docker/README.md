# =============================================================================
# AgriOS Docker Development Environment
# =============================================================================
# This folder contains Docker configuration for running all AgriOS services
# together for TOB-37, TOB-45, and TOB-46 testing.
#
# Services:
#   - CAS Service (gRPC: 50051, HTTP: 4000)
#   - Noti-Service (gRPC: 9012, HTTP: 8000)
#   - Supplier Service (gRPC: 9088, HTTP: 8088)
#   - Web API Gateway (HTTP: 4001)
# =============================================================================

## Quick Start

### Prerequisites

1. **Docker Desktop** running
2. **grpcurl** installed
3. **FCM credentials** file at `noti-service/config/fcm-dev-sdk.json`

### Step 1: Build Go Binaries

Since Docker image uses pre-built binaries (to avoid Azure DevOps auth issues), 
build them first:

**Windows PowerShell:**
```powershell
# Set environment for Linux build
$env:CGO_ENABLED="0"
$env:GOOS="linux"
$env:GOARCH="amd64"

# Build CAS
cd centre-auth-service
go build -o bin/cas-linux ./cmd/app/
cd ..

# Build Noti-Service
cd noti-service
go build -o bin/noti-linux ./cmd/main.go
cd ..

# Build Supplier Service
cd supplier-service
go build -o bin/supplier-linux ./cmd/main.go
cd ..

# Build Web API Gateway
cd web-api-gateway
go build -o bin/webgw-linux ./cmd/app/
cd ..
```

**Linux/macOS:**
```bash
# Build CAS
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o centre-auth-service/bin/cas-linux ./centre-auth-service/cmd/app/

# Build Noti-Service
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o noti-service/bin/noti-linux ./noti-service/cmd/main.go

# Build Supplier Service
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o supplier-service/bin/supplier-linux ./supplier-service/cmd/main.go

# Build Web API Gateway
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o web-api-gateway/bin/webgw-linux ./web-api-gateway/cmd/app/
```

### Step 2: Start Docker Services

```bash
# From repository root
docker compose -f docker/docker-compose.dev.yml up -d --build

# Wait for services to be healthy (~15-20 seconds)
sleep 20

# Check status
docker compose -f docker/docker-compose.dev.yml ps
```

### Step 3: Verify Services

```bash
# Check gRPC services
grpcurl -plaintext localhost:9012 list   # Noti-Service
grpcurl -plaintext localhost:50051 list  # CAS
grpcurl -plaintext localhost:9088 list   # Supplier Service

# Check HTTP health
curl http://localhost:8000/health  # Noti-Service
curl http://localhost:4000/health  # CAS
curl http://localhost:8088/health  # Supplier Service
curl http://localhost:4001/health  # Web API Gateway
```

### Step 4: Run Database Migrations

Apply the full schema from centre-auth-service migrations:

```bash
# Apply consolidated schema
cat centre-auth-service/migrations/final_schema.sql | docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth

# Apply additional migrations (062-070)
for file in centre-auth-service/migrations/0{62,63,64,65,66,67,68,69,70}*.sql; do
  cat "$file" | docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth
done

# Add missing column (if needed)
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c "ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS name TEXT;"
```

### Step 5: Seed Test Data

```bash
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth << 'EOF'
-- Test account for supplier
INSERT INTO accounts (id, type, identifier, password_hash, source, is_supplier, is_active_supplier, code)
VALUES (999, 'phone', '0909999999', '$2y$10$Gjw4QnR8fJJN2YlKnAZVDOBY0kBiIiv7OxmCMqanEEc6JECVE3hp2', 'app', true, true, 'TEST001')
ON CONFLICT (id) DO NOTHING;

-- Test supplier
INSERT INTO suppliers (id, account_id, company_name, status)
VALUES (888, 999, 'Test Supplier Company', 'approved')
ON CONFLICT (id) DO NOTHING;

-- Test user
INSERT INTO users (id, account_id, name, phone)
VALUES (999, 999, 'Test Supplier User', '0909999999')
ON CONFLICT (id) DO NOTHING;

-- Device session with FCM token placeholder
INSERT INTO device_sessions (id, account_id, device_id, firebase_token, is_active)
VALUES (1, 999, 'test-device-001', 'PLACEHOLDER_FCM_TOKEN', true)
ON CONFLICT (id) DO NOTHING;
EOF
```

### Step 6: Update FCM Token (Required for Testing)

Get a real FCM token from the mobile app and update the database:

```bash
# Update with real FCM token from mobile app
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c \
  "UPDATE device_sessions SET firebase_token = 'YOUR_REAL_FCM_TOKEN' WHERE account_id = 999;"

# Verify
docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth -c \
  "SELECT account_id, device_id, substring(firebase_token, 1, 30) as token_prefix, is_active FROM device_sessions;"
```

### Step 7: Test the Flow

**1. Login to get access token:**
```bash
grpcurl -plaintext -d '{"identifier": "0909999999", "password": "password123"}' \
  localhost:50051 auth.v1.AuthService/Login
```

**2. Test DeactiveSupplier (CAS -> Noti-Service -> FCM):**
```bash
# Use the accessToken from login response
TOKEN="YOUR_ACCESS_TOKEN"
grpcurl -plaintext -H "authorization: Bearer $TOKEN" \
  -d '{"id": 888}' localhost:50051 supplier.v1.SupplierService/DeactiveSupplier
```

**3. Direct test SendEventToDevices (Noti-Service):**
```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN"],
  "actionCode": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Test force logout"
}' localhost:9012 api.v1.NotificationService/SendEventToDevices
```

**4. Check logs for success:**
```bash
# Noti-service should show: "successfully sent fcm multicast. success: 1, failure: 0"
docker logs agrios_dev_noti --tail 20

# CAS should show: "deactivate notification sent successfully"
docker logs agrios_dev_cas --tail 20
```

---

## Verified Test Results (2025-12-25)

| Test Case | Result | Details |
|-----------|--------|---------|
| Login API | PASS | Account 999 (phone: 0909999999), password: password123 |
| DeactiveSupplier | PASS | Supplier 888 status toggled to `is_active_supplier: false` |
| CAS -> Noti-service gRPC | PASS | SendEventToDevices called with action_code=001 |
| FCM Multicast | PASS | success: 1, failure: 0 |
| Mobile App Notification | PASS | Push notification received on physical device |

**Test Environment:**
- Docker containers: postgres:17-alpine, redis:7-alpine, cas-service, noti-service
- FCM Token: Real token from mobile app (verified working)
- Test Account: 999 (phone: 0909999999)
- Test Supplier: 888 (Test Supplier Company)

---

## Services

| Service | Container | gRPC Port | HTTP Port |
|---------|-----------|-----------|-----------|
| PostgreSQL | agrios_dev_postgres | - | 5432 |
| Redis | agrios_dev_redis | - | 6379 |
| CAS | agrios_dev_cas | 50051 | 4000 |
| Noti-Service | agrios_dev_noti | 9012 | 8000 |
| Supplier Service | agrios_dev_supplier | 9088 | 8088 |
| Web API Gateway | agrios_dev_webgw | - | 4001 |

---

## Databases

| Database | Description |
|----------|-------------|
| `centre_auth` | CAS database with accounts, suppliers, device_sessions |
| `notification_service` | Notification database with notifications, templates |
| `supplier_svc_db` | Supplier service database with plant_types, stages, units, services |

---

## TOB-46: Supplier Service Testing

### Quick Test (After services are running)

```bash
# Test gRPC directly
grpcurl -plaintext localhost:9088 list
grpcurl -plaintext -d '{"page": 1, "size": 10}' localhost:9088 supplier_service.v1.PlantTypeService/GetListPlantTypes

# Test REST via Gateway
curl http://localhost:4001/api/v1/supplier/plant-types
curl http://localhost:4001/api/v1/supplier/stages
curl http://localhost:4001/api/v1/supplier/units
curl http://localhost:4001/api/v1/supplier/services

# Check service discovery
curl http://localhost:4001/api/discovery/services | jq '.data.services[] | select(.serviceName == "supplier-service")'
```

### Database Verification

```bash
# Check supplier service data
docker exec agrios_dev_postgres psql -U postgres -d supplier_svc_db -c "SELECT * FROM agrios.plant_types;"
docker exec agrios_dev_postgres psql -U postgres -d supplier_svc_db -c "SELECT * FROM agrios.stages;"
docker exec agrios_dev_postgres psql -U postgres -d supplier_svc_db -c "SELECT * FROM agrios.units;"
```

---

## Common Commands

### View Logs

```bash
# All services
docker compose -f docker/docker-compose.dev.yml logs -f

# Specific service
docker compose -f docker/docker-compose.dev.yml logs -f cas-service
docker compose -f docker/docker-compose.dev.yml logs -f noti-service
```

### Restart Services

```bash
# Restart all
docker compose -f docker/docker-compose.dev.yml restart

# Restart specific service
docker compose -f docker/docker-compose.dev.yml restart cas-service

# Rebuild and restart
docker compose -f docker/docker-compose.dev.yml up -d --build cas-service
```

### Stop Services

```bash
# Stop (keep data)
docker compose -f docker/docker-compose.dev.yml stop

# Stop and remove containers
docker compose -f docker/docker-compose.dev.yml down

# Full cleanup (remove volumes too)
docker compose -f docker/docker-compose.dev.yml down -v
```

### Database Access

```bash
# Connect to CAS database
docker exec -it agrios_dev_postgres psql -U postgres -d centre_auth

# Connect to Noti database
docker exec -it agrios_dev_postgres psql -U postgres -d notification_service
```

---

## Troubleshooting

### Binary not found

If you see errors about missing binary, rebuild:

```powershell
$env:CGO_ENABLED="0"; $env:GOOS="linux"; $env:GOARCH="amd64"
cd centre-auth-service && go build -o bin/cas-linux ./cmd/app/ && cd ..
cd noti-service && go build -o bin/noti-linux ./cmd/main.go && cd ..
docker compose -f docker/docker-compose.dev.yml up -d --build
```

### FCM credentials not found

Ensure `noti-service/config/fcm-dev-sdk.json` exists. Download from Firebase Console.

### Connection refused

Wait for services to be healthy. Check status:

```bash
docker compose -f docker/docker-compose.dev.yml ps
docker compose -f docker/docker-compose.dev.yml logs noti-service
```

### Database not initialized

If tables are missing, remove volumes and restart:

```bash
docker compose -f docker/docker-compose.dev.yml down -v
docker compose -f docker/docker-compose.dev.yml up -d --build
```

---

## Files Structure

```
docker/
  docker-compose.dev.yml     # Main compose file
  Dockerfile.cas.dev         # CAS Dockerfile
  Dockerfile.noti.dev        # Noti-Service Dockerfile
  Dockerfile.supplier.dev    # Supplier Service Dockerfile
  Dockerfile.webgw.dev       # Web API Gateway Dockerfile
  README.md                  # This file
  init-db/
    01_create_databases.sql  # Create databases (centre_auth, notification_service, supplier_svc_db)
    02_cas_schema.sh         # CAS schema migration
    03_noti_schema.sh        # Noti schema migration
    04_seed_test_data.sh     # Test data for TOB-37/45
    05_supplier_schema.sh    # Supplier service schema and seed data
```

---

## Related Documentation

- [TOB37_IMPLEMENTATION.md](../docs/tob37/TOB37_IMPLEMENTATION.md) - FCM Event System
- [TOB45_CAS_IMPLEMENTATION.md](../docs/tob45/TOB45_CAS_IMPLEMENTATION.md) - CAS Deactivation Flow
- [TOB46_IMPLEMENTATION.md](../docs/tob46/TOB46_IMPLEMENTATION.md) - Supplier Service Gateway Integration
