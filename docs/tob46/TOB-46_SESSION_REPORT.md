# TOB-46: Web API Gateway - Supplier Service Integration

**Author:** Development Team  
**Created:** 2025-12-25  
**Updated:** 2025-12-25
**Status:** MERGE READY - Proto package alignment completed

---

## 1. Executive Summary

Phiên làm việc này tập trung vào việc tích hợp supplier-service vào web-api-gateway. Vấn đề proto package mismatch giữa Core và supplier-service đã được giải quyết bằng cách migrate supplier-service sang sử dụng Core proto.

**Kết quả:**
- REST API endpoints cho supplier-service hoạt động qua web-api-gateway
- Supplier-service đã adopt Core proto (`supplier_service.v1`)
- Không còn replace directive - code merge-able vào main branch

---

## 2. Issues Encountered

### 2.1 Proto Package Mismatch (RESOLVED)

**Mô tả:**  
Core repository định nghĩa proto với package names khác với supplier-service thực tế sử dụng.

| Component | Package Names (Before) |
|-----------|------------------------|
| **Core proto** | `supplier_service.v1.PlantTypeService`, `supplier_service.v1.StageService`, etc. |
| **Supplier-service** | `planttype.v1.PlantTypeService`, `stage.v1.StageService`, `unit.v1.UnitService`, `service.v1.SupplierService` |

**Giải pháp (Implemented):**  
Migrate supplier-service để sử dụng Core proto trực tiếp:
```go
// Before
import servicev1 "agrios.vn/supplier-service/pkgs/pb/v1"

// After  
import servicev1 "dev.azure.com/agris-agriculture/Core/_git/Core.git/gen/go/proto/supplier_service/v1"
```

**Files updated:**
- `supplier-service/internal/transport/grpc.go`
- `supplier-service/internal/service/v1/*.go` (5 files)
- `supplier-service/go.mod` (added Core dependency)

---

### 2.2 JWT Token Type Mismatch

**Mô tả:**  
CAS service có 2 loại JWT tokens với secrets khác nhau:
- `secret_key_web` - cho accounts có `source=web`
- `secret_key_app` - cho accounts có `source=app`

Web-api-gateway gọi `VerifyTokenWeb` nhưng test accounts có `source=app`.

**Giải pháp:**  
Tạo accounts mới với `source=web` hoặc sử dụng đúng endpoint verify.

---

### 2.3 Docker Config Override Issue

**Mô tả:**  
Config file `config.yaml` sử dụng `localhost:50051` cho cas-service, không hoạt động trong Docker network.

Viper không thể override qua environment variables khi key chứa dấu gạch ngang (`-`):
```yaml
services:
  cas-service: "localhost:50051"  # Viper không map CAS_SERVICE env var
```

**Giải pháp:**  
Tạo file `config.docker.yaml` riêng với Docker hostnames và sử dụng `CONFIG_PATH` env var.

---

### 2.4 Casbin Rule Format Error

**Mô tả:**  
Casbin model yêu cầu 4 fields cho policy rule (`sub, dom, obj, act`) nhưng initial seed chỉ có 3 fields.

```
Error: invalid policy rule size: expected 4, got 3, rule: [admin * *]
```

**Giải pháp:**  
Sử dụng đúng format:
```sql
INSERT INTO casbin_rule (ptype, v0, v1, v2, v3) VALUES ('p', 'admin', '*', '*', '*');
```

---

### 2.5 Authorization Logic - Wildcard Access

**Mô tả:**  
CAS sử dụng `HasGlobalWildcardAccess()` để check permission, yêu cầu role = `*` trong domain = `*`, không phải role = `admin`.

**Giải pháp:**  
Thêm casbin rule với wildcard role:
```sql
INSERT INTO casbin_rule (ptype, v0, v1, v2) VALUES ('g', '8', '*', '*');
```

---

## 3. Changes Made

### 3.1 web-api-gateway Repository

| File | Change Type | Description |
|------|-------------|-------------|
| `go.mod` | Modified | Added `replace agrios.vn/supplier-service => ../supplier-service` |
| `go.sum` | Modified | Updated dependencies |
| `config/config.docker.yaml` | **NEW** | Docker-specific config with correct hostnames |
| `internal/router/api/v1.go` | Modified | Added `/supplier` route |
| `internal/grpc/service_clients.go` | Modified | Added `Conn *grpc.ClientConn` field |
| `internal/integrate/handler/supplier.go` | Modified | Uses DynamicSupplierHandler |
| `internal/integrate/handler/supplier_dynamic.go` | **NEW** | Dynamic handler with supplier-service proto types |

### 3.2 supplier-service Repository

| File | Change Type | Description |
|------|-------------|-------------|
| `config/config.yaml` | **NEW** | Local development config (not tracked in git) |
| `bin/supplier-linux` | **NEW** | Compiled binary (should be gitignored) |

### 3.3 centre-auth-service Repository

**Không có thay đổi code.** Chỉ có database seeds cho local testing.

---

## 4. Database Seeds (Local Only)

```sql
-- Database: centre_auth

-- Create admin role
INSERT INTO roles (code, name, description) 
VALUES ('admin', 'Administrator', 'Full system access');

-- Assign admin role to account 8
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES ('g', '8', 'admin', '*');

-- Admin policy - full access
INSERT INTO casbin_rule (ptype, v0, v1, v2, v3) 
VALUES ('p', 'admin', '*', '*', '*');

-- Wildcard access for account 8 (required by HasGlobalWildcardAccess)
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES ('g', '8', '*', '*');
```

---

## 5. Working Endpoints

Sau khi hoàn thành, các endpoints sau hoạt động qua web-api-gateway:

| Method | Endpoint | gRPC Service | gRPC Method |
|--------|----------|--------------|-------------|
| GET | `/api/v1/supplier/plant-types` | PlantTypeService | GetListPlantTypes |
| GET | `/api/v1/supplier/stages` | StageService | GetListStages |
| GET | `/api/v1/supplier/units` | UnitService | GetListUnits |
| GET | `/api/v1/supplier/services` | SupplierService | GetListServices |
| POST | `/api/v1/supplier/services` | SupplierService | CreateService |
| PUT | `/api/v1/supplier/services` | SupplierService | UpdateService |

---

## 6. Production Strategy - Discussion Required

### Option A: Supplier-service Adopts Core Proto (Recommended Long-term)

**Mô tả:**  
Thay đổi supplier-service để sử dụng proto từ Core repository thay vì proto riêng.

**Pros:**
- Consistent với kiến trúc proto-first
- Gateway sử dụng Core proto như các services khác
- Không cần workarounds

**Cons:**
- Breaking changes cho supplier-service
- Cần migration effort
- Ảnh hưởng đến các consumers hiện tại của supplier-service

**Effort:** Medium-High  
**Risk:** Medium

---

### Option B: Publish Supplier-service Proto as Module

**Mô tả:**  
Supplier-service publish proto types như Go module riêng, web-gateway import như dependency.

```go
// go.mod (production)
require agrios.vn/supplier-service v1.x.x
```

**Pros:**
- Không cần thay đổi supplier-service proto structure
- Gateway có thể import proto types

**Cons:**
- Cần setup Go module proxy/registry
- Thêm dependency management complexity
- Duplicate proto definitions (Core + supplier-service)

**Effort:** Medium  
**Risk:** Low

---

### Option C: Copy Proto Types to Gateway

**Mô tả:**  
Copy các proto types từ supplier-service vào web-gateway.

**Pros:**
- Quick fix
- Không cần external dependencies

**Cons:**
- Manual sync khi supplier-service thay đổi proto
- Dễ bị out of sync
- Violates DRY principle

**Effort:** Low  
**Risk:** High (maintenance burden)

---

## 7. Recommendations

1. **Không merge go.mod hiện tại vào main** - `replace` directive sẽ break CI/CD

2. **Short-term (để unblock development):**
   - Implement Option C (copy proto types)
   - Hoặc setup private Go module proxy cho Option B

3. **Long-term:**
   - Thực hiện Option A với proper migration plan
   - Align supplier-service proto với Core repository
   - Cần PO approval do breaking changes

4. **Documentation:**
   - Document JWT token types và usage
   - Document casbin model và rule format
   - Add proto naming conventions to copilot-instructions

---

## 8. Action Items

| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | Thảo luận production strategy với team | Tech Lead | HIGH |
| 2 | Quyết định Option A, B, hoặc C | PO + Tech Lead | HIGH |
| 3 | Revert/modify go.mod trước khi merge | Developer | HIGH |
| 4 | Document JWT token types | Developer | MEDIUM |
| 5 | Add migration scripts cho casbin rules | Developer | MEDIUM |
| 6 | Update copilot-instructions với proto conventions | Developer | LOW |

---

## 9. Test Account

Sử dụng cho testing qua web-api-gateway:

```
Email: developer@agrios.com
Password: password123
Account ID: 8
Source: web
Roles: admin (via casbin)
```

**Login command:**
```bash
curl -X POST http://localhost:4001/api/v1/cas/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"developer@agrios.com","password":"password123"}'
```

---

## 10. Appendix

### A. Proto Package Comparison

**Core proto (supplier_service.proto):**
```protobuf
package supplier_service.v1;
service PlantTypeService { ... }
service StageService { ... }
service UnitService { ... }
service SupplierService { ... }
```

**Supplier-service (plant_type.proto, stage.proto, etc.):**
```protobuf
// plant_type.proto
package planttype.v1;
service PlantTypeService { ... }

// stage.proto
package stage.v1;
service StageService { ... }

// unit.proto
package unit.v1;
service UnitService { ... }

// service.proto
package service.v1;
service SupplierService { ... }
```

### B. gRPC Method Path Mapping

| Gateway Expects | Supplier-service Actual |
|-----------------|------------------------|
| `/supplier_service.v1.PlantTypeService/GetListPlantTypes` | `/planttype.v1.PlantTypeService/GetListPlantTypes` |
| `/supplier_service.v1.StageService/GetListStages` | `/stage.v1.StageService/GetListStages` |
| `/supplier_service.v1.UnitService/GetListUnits` | `/unit.v1.UnitService/GetListUnits` |
| `/supplier_service.v1.SupplierService/GetListServices` | `/service.v1.SupplierService/GetListServices` |

---

**End of Report**
