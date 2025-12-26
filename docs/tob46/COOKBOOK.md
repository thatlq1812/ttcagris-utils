# TOB-46 Supplier Service Integration Cookbook

**Author:** AI Assistant  
**Created:** 2025-12-25  
**Last Updated:** 2025-12-25

This cookbook provides step-by-step instructions to run and test the supplier-service integration with web-api-gateway.

---

## Prerequisites

- Docker and Docker Compose installed
- `grpcurl` installed (for gRPC testing)
- `curl` and `jq` installed (for REST API testing)

---

## 1. Start Services

### Option A: Start All Services

```bash
cd d:/ttcagris/docker
docker compose -f docker-compose.dev.yml up -d
```

### Option B: Start Individual Services

```bash
# Start infrastructure first
docker compose -f docker-compose.dev.yml up -d postgres redis

# Wait for postgres to be ready, then start services
docker compose -f docker-compose.dev.yml up -d cas supplier web-api-gateway
```

### Verify Services Running

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected output:
```
NAMES                 STATUS              PORTS
agrios_dev_webgw      Up (healthy)        0.0.0.0:4001->4001/tcp
agrios_dev_supplier   Up (healthy)        0.0.0.0:8088->8088/tcp, 0.0.0.0:9088->9088/tcp
agrios_dev_cas        Up (healthy)        0.0.0.0:4000->4000/tcp, 0.0.0.0:50051->50051/tcp
agrios_dev_postgres   Up (healthy)        0.0.0.0:5432->5432/tcp
agrios_dev_redis      Up (healthy)        0.0.0.0:6379->6379/tcp
```

---

## 2. Test gRPC Endpoints (Direct to Supplier Service)

### List Available Services

```bash
grpcurl -plaintext localhost:9088 list
```

### Get Plant Types

```bash
grpcurl -plaintext localhost:9088 supplier_service.v1.PlantTypeService/GetListPlantTypes
```

### Get Stages

```bash
grpcurl -plaintext localhost:9088 supplier_service.v1.StageService/GetListStages
```

### Get Units

```bash
grpcurl -plaintext localhost:9088 supplier_service.v1.UnitService/GetListUnits
```

### Get Plant Type by ID

```bash
grpcurl -plaintext -d '{"id": 1}' localhost:9088 supplier_service.v1.PlantTypeService/GetPlantType
```

---

## 3. Test REST API Endpoints (via Web Gateway)

### Step 1: Get Authentication Token

```bash
# Save token to environment variable (using admin account)
export TOKEN=$(grpcurl -plaintext -d '{"identifier":"developer@agrios.com","password":"password123"}' localhost:50051 auth.v1.AuthService/Login 2>/dev/null | jq -r '.data.accessToken')

# Verify token was obtained
echo "Token: ${TOKEN:0:50}..."
```

### Step 2: Test Endpoints

#### Get Plant Types

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4001/api/v1/supplier/plant-types | jq .
```

#### Get Stages

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4001/api/v1/supplier/stages | jq .
```

#### Get Units

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4001/api/v1/supplier/units | jq .
```

#### Get Plant Type by ID

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4001/api/v1/supplier/plant-types/1 | jq .
```

---

## 4. Quick Test Script (Copy-Paste Ready)

### Full Test - gRPC and REST

```bash
# Test gRPC
echo "=== gRPC Tests ===" && \
grpcurl -plaintext localhost:9088 supplier_service.v1.PlantTypeService/GetListPlantTypes | jq -r '"PlantTypes: " + .code + " - " + .message' && \
grpcurl -plaintext localhost:9088 supplier_service.v1.StageService/GetListStages | jq -r '"Stages: " + .code + " - " + .message' && \
grpcurl -plaintext localhost:9088 supplier_service.v1.UnitService/GetListUnits | jq -r '"Units: " + .code + " - " + .message' && \

# Test REST API (using admin account)
echo "" && echo "=== REST API Tests ===" && \
export TOKEN=$(grpcurl -plaintext -d '{"identifier":"developer@agrios.com","password":"password123"}' localhost:50051 auth.v1.AuthService/Login 2>/dev/null | jq -r '.data.accessToken') && \
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4001/api/v1/supplier/plant-types | jq -r '"PlantTypes: " + .code + " - " + .message + " (" + (.data.total|tostring) + " items)"' && \
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4001/api/v1/supplier/stages | jq -r '"Stages: " + .code + " - " + .message + " (" + (.data.total|tostring) + " items)"' && \
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:4001/api/v1/supplier/units | jq -r '"Units: " + .code + " - " + .message + " (" + (.data.total|tostring) + " items)"'
```

Expected output:
```
=== gRPC Tests ===
PlantTypes: 000 - success
Stages: 000 - success
Units: 000 - success

=== REST API Tests ===
PlantTypes: 000 - success (4 items)
Stages: 000 - success (4 items)
Units: 000 - success (4 items)
```

---

## 5. Available Endpoints

### REST API Endpoints (Web Gateway - Port 4001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/supplier/plant-types` | List all plant types |
| GET | `/api/v1/supplier/plant-types/:id` | Get plant type by ID |
| GET | `/api/v1/supplier/stages` | List all stages |
| GET | `/api/v1/supplier/stages/:id` | Get stage by ID |
| GET | `/api/v1/supplier/units` | List all units |
| GET | `/api/v1/supplier/units/:id` | Get unit by ID |

### gRPC Services (Supplier Service - Port 9088)

| Service | Methods |
|---------|---------|
| `supplier_service.v1.PlantTypeService` | `GetListPlantTypes`, `GetPlantType` |
| `supplier_service.v1.StageService` | `GetListStages`, `GetStage` |
| `supplier_service.v1.UnitService` | `GetListUnits`, `GetUnit` |
| `supplier_service.v1.SupplierService` | `GetListSuppliers`, `GetSupplier` |
| `supplier_service.v1.EquipmentService` | `GetListEquipments`, `GetEquipment` |

---

## 6. Troubleshooting

### Token Expired

If you get `"invalid or expired token"`, refresh the token:

```bash
export TOKEN=$(grpcurl -plaintext -d '{"identifier":"developer@agrios.com","password":"password123"}' localhost:50051 auth.v1.AuthService/Login 2>/dev/null | jq -r '.data.accessToken')
```

### Permission Denied

If you get `"Không có quyền truy cập"`, the account needs casbin permissions:

```bash
docker exec agrios_dev_postgres psql -U postgres -d centre_auth -c "INSERT INTO casbin_rule (ptype, v0, v1, v2) VALUES ('g', '2', '*', '*');"
docker restart agrios_dev_cas
```

### Service Connection Failed

Check if services are running:

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}"
```

Check service logs:

```bash
docker logs agrios_dev_supplier --tail 20
docker logs agrios_dev_webgw --tail 20
docker logs agrios_dev_cas --tail 20
```

### CAS Panic on Login

If CAS crashes when logging in, the account may be missing a user record:

```bash
# Check if user exists
docker exec agrios_dev_postgres psql -U postgres -d centre_auth -c "SELECT a.id, a.identifier, u.id as user_id FROM accounts a LEFT JOIN users u ON u.account_id = a.id WHERE a.identifier = 'supplier@agrios.com';"

# If user_id is NULL, create user record
docker exec agrios_dev_postgres psql -U postgres -d centre_auth -c "INSERT INTO users (account_id, name, email, is_deleted, created_at, updated_at) VALUES (2, 'Supplier User', 'supplier@agrios.com', false, NOW(), NOW());"
```

---

## 7. Rebuild Services (After Code Changes)

### Rebuild Supplier Service

```bash
cd d:/ttcagris/supplier-service
set GOOS=linux&& set GOARCH=amd64&& go build -mod=vendor -o bin/supplier-linux ./cmd/app
docker restart agrios_dev_supplier
```

### Rebuild Web Gateway

```bash
cd d:/ttcagris/web-api-gateway
set GOOS=linux&& set GOARCH=amd64&& go build -mod=vendor -o bin/webgw-linux ./cmd/app
docker restart agrios_dev_webgw
```

---

## 8. Sample Response Data

### Plant Types Response

```json
{
  "code": "000",
  "message": "success",
  "data": {
    "items": [
      {"id": 1, "name": "Mía", "created_at": "2025-12-25T13:07:36Z", "updated_at": "2025-12-25T13:07:36Z"},
      {"id": 2, "name": "Chuối", "created_at": "2025-12-25T13:07:36Z", "updated_at": "2025-12-25T13:07:36Z"},
      {"id": 3, "name": "Dừa", "created_at": "2025-12-25T13:07:36Z", "updated_at": "2025-12-25T13:07:36Z"},
      {"id": 4, "name": "Lúa", "created_at": "2025-12-25T13:07:36Z", "updated_at": "2025-12-25T13:07:36Z"}
    ],
    "total": 4,
    "page": 1,
    "size": 10,
    "has_more": false
  }
}
```

### Stages Response

```json
{
  "code": "000",
  "message": "success",
  "data": {
    "items": [
      {"id": 1, "name": "Chuẩn bị đất", "display_order": 1, "is_active": true},
      {"id": 2, "name": "Trồng trọt", "display_order": 2, "is_active": true},
      {"id": 3, "name": "Chăm sóc", "display_order": 3, "is_active": true},
      {"id": 4, "name": "Thu hoạch", "display_order": 4, "is_active": true}
    ],
    "total": 4,
    "page": 1,
    "size": 10
  }
}
```

### Units Response

```json
{
  "code": "000",
  "message": "success",
  "data": {
    "items": [
      {"id": 1, "name": "Diện tích", "type": ["m2", "km2", "ha", "công"]},
      {"id": 2, "name": "Khối lượng", "type": ["kg", "tấn", "gam"]},
      {"id": 3, "name": "Thể tích", "type": ["l", "m3", "ml"]},
      {"id": 4, "name": "Thời gian", "type": ["giờ", "ngày", "tuần"]}
    ],
    "total": 4,
    "page": 1,
    "size": 10
  }
}
```
