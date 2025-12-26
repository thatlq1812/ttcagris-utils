# FCM Integration Guide: From Noti-Service to CAS and Gateway

**Author:** AI Assistant  
**Created:** 2024-12-24  
**Last Updated:** 2024-12-24  
**Status:** Implementation In Progress (70% Complete)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Current State Analysis](#2-current-state-analysis)
3. [Phase 1: Update Core Proto](#3-phase-1-update-core-proto)
4. [Phase 2: Implement in CAS](#4-phase-2-implement-in-cas)
5. [Phase 3: Gateway Integration](#5-phase-3-gateway-integration)
6. [Testing Strategy](#6-testing-strategy)
7. [Troubleshooting](#7-troubleshooting)
8. [Checklist: Start Implementation Now](#8-checklist-start-implementation-now)

---

## 1. Overview

### 1.1 Goal

Tích hợp FCM event pushing từ Noti-Service vào Centre-Auth-Service (CAS) để thực hiện:

- **Force Logout**: Khi admin deactivate supplier/farmer, gửi event đến tất cả device của user đó để force logout.
- **Session Invalidation**: Khi user thay đổi password hoặc bị revoke quyền, thông báo đến các device.

### 1.2 Implementation Progress

**Completed (70%):**
- ✅ Core proto updated with SendEventToDevices RPC
- ✅ Generated Go code from proto files
- ✅ NotificationClient methods implemented (SendEventToDevices, SendForceLogoutEvent)
- ✅ SupplierUsecase updated with FCM integration
- ✅ DeviceSessionRepository dependency added
- ✅ Dependency injection configured
- ✅ Local Docker testing infrastructure created

**Remaining (30%):**
- ⏳ Local integration testing
- ⏳ Mobile app FCM verification
- ⏳ Core PR merge to main
- ⏳ CAS PR creation and review

### 1.3 Strengths of This Plan

Plan này đã đi đúng trình tự chuẩn cho Microservices integration: **Contract (Proto) -> Client -> Business Logic -> Data Access -> Dependency Injection.**

**Key Advantages:**

* **Data Flow Logic:** Hiểu rõ CAS chỉ có `account_id`, nhưng Noti-service cần `device_tokens`. Query `DeviceSession` là bước quan trọng để tính năng hoạt động.
* **Safe Sequence:** Update Proto trước -> Regenerate code -> Sửa logic. Tránh lỗi compile do thiếu hàm.
* **Accurate Queries:** Query `firebase_token` với điều kiện `is_active = true` tránh gửi tin nhầm đến các device đã logout.

### 1.3 Architecture Flow

```
                                    +-----------------+
                                    |   Mobile App    |
                                    |  (FCM Client)   |
                                    +--------^--------+
                                             |
                                             | FCM Push
                                             |
+----------------+     gRPC      +-----------+-----------+
|  API Gateway   | ------------> |    Noti-Service       |
+----------------+               |  SendEventToDevices   |
        |                        +-----------------------+
        | REST                              ^
        v                                   | gRPC
+----------------+                          |
| Centre-Auth    |--------------------------+
| Service (CAS)  |
+----------------+
        |
        v
+----------------+
|   PostgreSQL   |
| device_sessions|
+----------------+
```

### 1.4 Key Components

| Component | Responsibility |
|-----------|---------------|
| **Core Proto** | Định nghĩa `SendEventToDevices` RPC |
| **Noti-Service** | Xử lý FCM push, đã hoàn thành |
| **CAS** | Gọi Noti-Service sau khi deactivate user |
| **Gateway** | Forward REST request (optional changes) |

---

## 2. Current State Analysis

### 2.1 Noti-Service (COMPLETED)

Proto tại `noti-service/internal/api/v1/notification.proto`:

```protobuf
service NotificationService {
  // ... existing RPCs
  rpc SendEventToDevices(SendEventToDevicesRequest) returns (BaseResponse) {}
}

message SendEventToDevicesRequest {
  repeated string device_tokens = 1 [(buf.validate.field).repeated.min_items = 1];
  string action_code = 2 [(buf.validate.field).string.min_len = 1];
  string model = 3 [(buf.validate.field).string.min_len = 1];
  string action = 4 [(buf.validate.field).string.min_len = 1];
  string description = 5;
  map<string, string> data = 6;
}
```

### 2.2 CAS (NEEDS UPDATE)

**Already have:**
- `NotificationClient` tại `pkg/grpcclient/notification_client.go`
- `DeviceSession` domain với `FirebaseToken`
- `DeviceSessionRepository` với `GetActiveByAccountID`
- `SupplierUsecase.DeactiveSupplier()` - cần thêm FCM call

**Missing:**
- Method `SendEventToDevices` trong `NotificationClient`
- Logic gọi FCM sau khi deactivate

### 2.3 Core Proto (NEEDS UPDATE)

Proto tại `Core/proto/notification/v1/notification.proto` **CHƯA CÓ** `SendEventToDevices`.

---

## 3. Phase 1: Update Core Proto

### 3.1 Sync Proto Files

**CRITICAL FIRST STEP:** Đảm bảo file proto trong Core repo đã có đủ định nghĩa mới nhất từ noti-service.

**Option A: Copy from noti-service (if separated)**
```bash
# Nếu Core và noti-service dùng chung proto files
cp noti-service/internal/api/v1/notification.proto Core/proto/notification/v1/
```

**Option B: Edit directly in Core**
Nếu Core là single source of truth cho tất cả proto, thì sửa trực tiếp trong Core.

### 3.2 Edit Proto File

**File:** `Core/proto/notification/v1/notification.proto`

Thêm vào service definition:

```protobuf
service NotificationService {
  // ... existing RPCs ...
  
  // FCM Event Push - Data-only message for background wake-up
  rpc SendEventToDevices(SendEventToDevicesRequest) returns (BaseResponse) {}
  rpc SendNotificationToDevices(SendNotificationToDevicesRequest) returns (BaseResponse) {}
  rpc SendNotificationToTopic(SendNotificationToTopicRequest) returns (BaseResponse) {}
}
```

Thêm message definition (sau `SendNotificationToDevicesRequest`):

```protobuf
// SendEventToDevicesRequest - Data-only FCM message for background events
// Used for: Force Logout, Session Invalidation, Silent Updates
message SendEventToDevicesRequest {
  repeated string device_tokens = 1 [(buf.validate.field).repeated.min_items = 1];
  string action_code = 2 [(buf.validate.field).string.min_len = 1]; // e.g., "FORCE_LOGOUT", "SESSION_EXPIRED"
  string model = 3 [(buf.validate.field).string.min_len = 1];       // e.g., "supplier", "farmer", "account"
  string action = 4 [(buf.validate.field).string.min_len = 1];      // e.g., "deactivated", "password_changed"
  string description = 5;                                           // Human-readable description
  map<string, string> data = 6;                                     // Additional metadata
}
```

### 3.3 Generate Go Code

```bash
cd Core
make generate
```

### 3.4 Commit and Push

```bash
git add .
git commit -m "feat(notification): add SendEventToDevices RPC for FCM events"
git push origin main
```

### 3.5 Update Services

**Trong CAS:**

```bash
cd centre-auth-service
make update-core
# hoặc
go get dev.azure.com/agris-agriculture/Core/_git/Core.git@latest
go mod tidy
```

**Trong Gateway (nếu cần):**

```bash
cd app-api-gateway
make update-core
go mod tidy
```

---

## 4. Phase 2: Implement in CAS

### 4.1 Add SendEventToDevices Method to NotificationClient

**File:** `centre-auth-service/pkg/grpcclient/notification_client.go`

Thêm method mới:

```go
// EventCode constants for FCM events
const (
    EventCodeForceLogout     = "FORCE_LOGOUT"
    EventCodeSessionExpired  = "SESSION_EXPIRED"
    EventCodePasswordChanged = "PASSWORD_CHANGED"
    EventCodeAccountUpdated  = "ACCOUNT_UPDATED"
)

// SendEventToDevicesRequest represents the request to send FCM event
type SendEventToDevicesRequest struct {
    DeviceTokens []string
    ActionCode   string
    Model        string
    Action       string
    Description  string
    Data         map[string]string
}

// SendEventToDevices sends a data-only FCM message to wake up devices
// This is used for silent events like Force Logout, Session Invalidation
func (c *NotificationClient) SendEventToDevices(
    ctx context.Context,
    req *SendEventToDevicesRequest,
) (*notificationv1.BaseResponse, error) {
    if len(req.DeviceTokens) == 0 {
        return nil, fmt.Errorf("device tokens cannot be empty")
    }
    if strings.TrimSpace(req.ActionCode) == "" {
        return nil, fmt.Errorf("action code cannot be empty")
    }
    if strings.TrimSpace(req.Model) == "" {
        return nil, fmt.Errorf("model cannot be empty")
    }
    if strings.TrimSpace(req.Action) == "" {
        return nil, fmt.Errorf("action cannot be empty")
    }

    ctx, cancel := context.WithTimeout(ctx, c.timeout)
    defer cancel()

    protoReq := &notificationv1.SendEventToDevicesRequest{
        DeviceTokens: req.DeviceTokens,
        ActionCode:   req.ActionCode,
        Model:        req.Model,
        Action:       req.Action,
        Description:  req.Description,
        Data:         req.Data,
    }

    resp, err := c.notificationClient.SendEventToDevices(ctx, protoReq)
    if err != nil {
        c.logger.Error("failed to send event to devices",
            zap.Strings("device_tokens", req.DeviceTokens),
            zap.String("action_code", req.ActionCode),
            zap.String("model", req.Model),
            zap.Error(err))
        return nil, fmt.Errorf("failed to send event: %w", err)
    }

    if resp.FailureCount > 0 {
        c.logger.Warn("some devices failed to receive event",
            zap.Int32("success_count", resp.SuccessCount),
            zap.Int32("failure_count", resp.FailureCount),
            zap.Strings("failed_tokens", resp.FailedTokens))
    }

    c.logger.Info("event sent to devices",
        zap.Int32("success_count", resp.SuccessCount),
        zap.Int32("failure_count", resp.FailureCount),
        zap.String("action_code", req.ActionCode))

    return resp, nil
}

// SendForceLogoutEvent is a convenience method to send force logout event
func (c *NotificationClient) SendForceLogoutEvent(
    ctx context.Context,
    deviceTokens []string,
    model string,       // "supplier", "farmer", "account"
    reason string,      // "deactivated", "deleted", "suspended"
    accountID int64,
) (*notificationv1.BaseResponse, error) {
    return c.SendEventToDevices(ctx, &SendEventToDevicesRequest{
        DeviceTokens: deviceTokens,
        ActionCode:   EventCodeForceLogout,
        Model:        model,
        Action:       reason,
        Description:  fmt.Sprintf("%s has been %s", model, reason),
        Data: map[string]string{
            "account_id": fmt.Sprintf("%d", accountID),
            "timestamp":  time.Now().UTC().Format(time.RFC3339),
        },
    })
}
```

### 4.2 Update SupplierUsecase

**File:** `centre-auth-service/internal/usecase/supplier_usecase.go`

Cập nhật method `DeactiveSupplier`:

```go
func (uc *supplierUsecase) DeactiveSupplier(ctx context.Context, supplierID int64) (bool, error) {
    uc.logger.Info("DeactiveSupplier started",
        zap.Int64("supplier_id", supplierID))

    // Get supplier first
    supplier, err := uc.supplierRepo.FindByID(ctx, supplierID)
    if err != nil {
        uc.logger.Error("Failed to get supplier",
            zap.Int64("supplier_id", supplierID),
            zap.Error(err))
        return false, fmt.Errorf("failed to get supplier: %w", err)
    }

    if supplier == nil {
        uc.logger.Warn("Supplier not found",
            zap.Int64("supplier_id", supplierID))
        return false, fmt.Errorf("supplier not found")
    }

    if supplier.AccountID == nil {
        uc.logger.Error("Supplier has no associated account",
            zap.Int64("supplier_id", supplierID))
        return false, fmt.Errorf("supplier has no associated account")
    }

    accountID := *supplier.AccountID

    // Get account by ID
    account, err := uc.accountRepo.GetByID(ctx, accountID)
    if err != nil {
        uc.logger.Error("Failed to get account",
            zap.Int64("supplier_id", supplierID),
            zap.Int64("account_id", accountID),
            zap.Error(err))
        return false, fmt.Errorf("failed to get account: %w", err)
    }

    // Toggle is_active_supplier
    oldStatus := account.IsActiveSupplier
    newIsActiveSupplier := !account.IsActiveSupplier
    account.IsActiveSupplier = newIsActiveSupplier

    // Update account
    if err := uc.accountRepo.Update(ctx, accountID, account); err != nil {
        uc.logger.Error("Failed to update account",
            zap.Int64("supplier_id", supplierID),
            zap.Int64("account_id", accountID),
            zap.Bool("old_status", oldStatus),
            zap.Bool("new_status", newIsActiveSupplier),
            zap.Error(err))
        return false, fmt.Errorf("failed to update account: %w", err)
    }

    // === NEW: Send Force Logout Event if deactivating ===
    if !newIsActiveSupplier {
        go uc.sendForceLogoutEvent(context.Background(), accountID, "supplier", "deactivated")
    }

    uc.logger.Info("DeactiveSupplier completed successfully",
        zap.Int64("supplier_id", supplierID),
        zap.Int64("account_id", accountID),
        zap.Bool("old_status", oldStatus),
        zap.Bool("new_status", newIsActiveSupplier))

    return newIsActiveSupplier, nil
}

// sendForceLogoutEvent sends FCM event to all active devices of an account
// This runs in background goroutine to not block the main request
// CRITICAL: This function should NEVER fail the parent transaction
func (uc *supplierUsecase) sendForceLogoutEvent(ctx context.Context, accountID int64, model, reason string) {
    // Guard: Check if notification client is configured
    if uc.notificationClient == nil {
        uc.logger.Warn("notification client not configured, skipping force logout event",
            zap.Int64("account_id", accountID))
        return
    }

    // Get all active device sessions for this account
    sessions, err := uc.deviceSessionRepo.GetActiveByAccountID(ctx, accountID)
    if err != nil {
        // Log error but DO NOT propagate - FCM is best-effort
        uc.logger.Error("failed to get active device sessions",
            zap.Int64("account_id", accountID),
            zap.Error(err))
        return
    }

    // Early exit: No active sessions
    if len(sessions) == 0 {
        uc.logger.Info("no active device sessions found, skipping force logout event",
            zap.Int64("account_id", accountID))
        return
    }

    // Collect Firebase tokens
    var deviceTokens []string
    for _, session := range sessions {
        if session.FirebaseToken != nil && *session.FirebaseToken != "" {
            deviceTokens = append(deviceTokens, *session.FirebaseToken)
        }
    }

    // Early exit: No valid tokens (CRITICAL CHECK)
    if len(deviceTokens) == 0 {
        uc.logger.Info("no Firebase tokens found for active sessions",
            zap.Int64("account_id", accountID),
            zap.Int("session_count", len(sessions)))
        return
    }

    // Send force logout event (best-effort, errors are logged only)
    resp, err := uc.notificationClient.SendForceLogoutEvent(ctx, deviceTokens, model, reason, accountID)
    if err != nil {
        // Log error but DO NOT return error - FCM failure should not fail deactivation
        uc.logger.Error("failed to send force logout event",
            zap.Int64("account_id", accountID),
            zap.Strings("device_tokens", deviceTokens),
            zap.Error(err))
        return
    }

    uc.logger.Info("force logout event sent successfully",
        zap.Int64("account_id", accountID),
        zap.Int32("success_count", resp.SuccessCount),
        zap.Int32("failure_count", resp.FailureCount))
}
```

### 4.3 Update SupplierUsecase Dependencies

**File:** `centre-auth-service/internal/usecase/supplier_usecase.go`

Cập nhật struct và constructor:

```go
type supplierUsecase struct {
    supplierRepo       repository.SupplierRepository
    accountRepo        repository.AccountRepository
    deviceSessionRepo  repository.DeviceSessionRepository  // NEW
    notificationClient *grpcclient.NotificationClient
    tracker            *audit.Tracker
    logger             *zap.Logger
}

// NewSupplierUsecase creates a new supplier usecase
func NewSupplierUsecase(
    supplierRepo repository.SupplierRepository,
    accountRepo repository.AccountRepository,
    deviceSessionRepo repository.DeviceSessionRepository,  // NEW
    notificationClient *grpcclient.NotificationClient,
    auditRepo repository.AuditLogRepository,
    logger *zap.Logger,
) SupplierUsecase {
    return &supplierUsecase{
        supplierRepo:       supplierRepo,
        accountRepo:        accountRepo,
        deviceSessionRepo:  deviceSessionRepo,  // NEW
        notificationClient: notificationClient,
        tracker:            audit.NewTracker(auditRepo, logger),
        logger:             logger,
    }
}
```

### 4.4 Update Dependency Injection

**File:** `centre-auth-service/internal/api/init.go`

Tìm và cập nhật nơi tạo `SupplierUsecase`:

```go
SupplierUsecase: usecase.NewSupplierUsecase(
    repos.Supplier,
    repos.Account,
    repos.DeviceSession,  // NEW - add DeviceSession repository
    d.GRPCClients.Notification,
    repos.AuditLog,
    d.Logger,
),
```

### 4.5 Critical Implementation Notes

#### A. Empty Token Handling

**Scenario:** User chưa bao giờ login app (hoặc đã logout hết), danh sách tokens rỗng.

**Solution:** Check `len(deviceTokens) == 0` ngay lập tức và return sớm. Đừng gọi Noti-service với list rỗng.

```go
if len(deviceTokens) == 0 {
    uc.logger.Info("no Firebase tokens found, skipping FCM event")
    return // Early exit
}
```

#### B. Error Handling Strategy

**Critical Principle:** Deactivate Supplier là nghiệp vụ quan trọng (liên quan tiền/pháp lý), còn gửi Noti là phụ trợ (UX).

**Rules:**
1. **DB Transaction:** Nếu lỗi DB -> Return error, rollback
2. **FCM Push:** Nếu lỗi FCM -> Log warning ONLY, DO NOT return error
3. **Async Execution:** Chạy FCM trong goroutine để không block response cho Admin

```go
// CORRECT PATTERN
// Step 1: Critical business logic (must succeed)
if err := uc.accountRepo.Update(ctx, accountID, account); err != nil {
    return false, fmt.Errorf("failed to update account: %w", err)  // FAIL HARD
}

// Step 2: Auxiliary notification (best-effort)
if !newIsActiveSupplier {
    go uc.sendForceLogoutEvent(context.Background(), accountID, "supplier", "deactivated")
    // Note: Using context.Background() to avoid cancellation from parent request
}
```

**Anti-pattern (WRONG):**
```go
// WRONG: Don't do this
if err := uc.sendForceLogoutEvent(...); err != nil {
    return false, err  // This would rollback deactivation!
}
```

#### C. Proto Synchronization

**Critical:** Đảm bảo file proto trong Core đã có định nghĩa `SendEventToDevices` trước khi generate.

**Verification:**
```bash
# Check if RPC exists in Core proto
grep -n "SendEventToDevices" Core/proto/notification/v1/notification.proto

# Should output something like:
# 17:  rpc SendEventToDevices(SendEventToDevicesRequest) returns (BaseResponse) {}
```

**Common Mistake:** Quên copy proto từ noti-service, dẫn đến code sinh ra không có hàm mới.

---

## 5. Phase 3: Gateway Integration

### 5.1 Current State

Gateway đã có endpoint:
- `DELETE /api/v1/cas/accounts/deactive` - Deactivate account

Endpoint này forward request đến CAS, và CAS sẽ xử lý FCM internally.

### 5.2 Changes Required (Optional)

**Không cần thay đổi Gateway** nếu:
- Gateway chỉ forward request đến CAS
- CAS xử lý toàn bộ logic (database update + FCM push)

**Cần thay đổi Gateway** nếu:
- Gateway cần validate response có FCM result
- Gateway cần log FCM push status

### 5.3 Optional: Add Logging for FCM Events

Nếu muốn track FCM events tại Gateway level, thêm logging:

**File:** `app-api-gateway/internal/integrate/services/cas.go`

```go
// Trong handler cua deactivate endpoint
RestRoute(integrate.DELETE, "/api/v1/cas/accounts/deactive",
    integrate.NewGenericRouteHandler(
        "DeactiveAccount",
        "/account.v1.AccountService/DeactiveAccount",
        // ... existing config
    ).WithPostProcess(func(ctx *fiber.Ctx, resp interface{}) error {
        // Log response for monitoring
        aglog.Infof("deactivate account completed, FCM events triggered in background")
        return nil
    }),
),
```

---

## 6. Testing Checklist

### 6.1 Unit Tests

**File:** `centre-auth-service/pkg/grpcclient/notification_client_test.go`

```go
func TestSendEventToDevices(t *testing.T) {
    // Mock gRPC client
    // Test cases:
    // 1. Success case - all tokens receive event
    // 2. Partial failure - some tokens fail
    // 3. Empty tokens - should return error
    // 4. Timeout handling
}

func TestSendForceLogoutEvent(t *testing.T) {
    // Test convenience method
}
```

### 6.2 Integration Tests

```bash
# 1. Start services
cd noti-service && make api
cd centre-auth-service && make api

# 2. Test gRPC directly
grpcurl -plaintext \
  -d '{
    "device_tokens": ["test-token-1"],
    "action_code": "FORCE_LOGOUT",
    "model": "supplier",
    "action": "deactivated",
    "description": "Supplier deactivated by admin"
  }' \
  localhost:9012 api.v1.NotificationService/SendEventToDevices

# 3. Test via CAS (need valid supplier)
curl -X DELETE \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  http://localhost:4000/api/v1/suppliers/{supplier_id}/deactivate
```

### 6.3 Mobile App Testing

1. **Setup:**
   - Cài app trên device thật
   - Login với supplier account
   - Verify Firebase token được lưu vào `device_sessions` table

2. **Test Force Logout:**
   - Dùng admin account deactivate supplier
   - Kiểm tra app nhận được FCM data message
   - Verify app xử lý logout correctly

3. **Edge Cases:**
   - Test khi app ở background
   - Test khi app bị kill
   - Test multiple devices cùng account

---

## 7. Troubleshooting

### 7.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Proto generation fails | Missing `SendEventToDevices` in Core | Update Core proto first |
| Import not found | Core not updated | Run `make update-core` |
| FCM not sent | Notification client nil | Check config `services.notification` |
| Device not waking up | Missing APNS/Android config | Check FCM adapter config |
| Tokens empty | No active sessions | Verify login saves Firebase token |

### 7.2 Debug Logging

Thêm debug logging:

```go
uc.logger.Debug("preparing force logout event",
    zap.Int64("account_id", accountID),
    zap.Int("session_count", len(sessions)),
    zap.Int("token_count", len(deviceTokens)),
    zap.Strings("tokens", deviceTokens))
```

### 7.3 Verify Database

```sql
-- Check device sessions with Firebase tokens
SELECT 
    account_id, 
    device_id, 
    firebase_token, 
    is_active,
    last_active_at
FROM device_sessions 
WHERE account_id = <account_id>
  AND is_active = true
  AND firebase_token IS NOT NULL;
```

### 7.4 Monitor FCM Response

Kiểm tra logs của Noti-Service:

```bash
# Filter FCM related logs
docker logs noti-service 2>&1 | grep -i "fcm\|firebase\|event"
```

---

## 8. Checklist: Start Implementation Now

## 8. Checklist: Start Implementation Now

### Quick Start Checklist

Đã đọc và hiểu plan? Bắt đầu ngay với checklist này:

- [x] **Step 1: Verify Proto Sync**
  ```bash
  # Kiểm tra xem Core proto đã có SendEventToDevices chưa
  cd Core
  grep "SendEventToDevices" proto/notification/v1/notification.proto
  ```
  ✅ **COMPLETED** - Proto đã có `SendEventToDevices` RPC

- [x] **Step 2: Copy Proto (if needed)**
  ```bash
  # Nếu Core chưa có, copy từ noti-service
  cp noti-service/internal/api/v1/notification.proto Core/proto/notification/v1/
  ```
  ✅ **SKIPPED** - Proto đã có sẵn

- [x] **Step 3: Generate Proto**
  ```bash
  cd Core
  buf generate
  # Verify: Check gen/go/proto/notification/v1/ for new methods
  ```
  ✅ **COMPLETED** - Code generated successfully

- [x] **Step 4: Update CAS Dependencies**
  ```bash
  cd centre-auth-service
  go get dev.azure.com/agris-agriculture/Core/_git/Core.git@add/tob37-sent-event-action-to-mobileapp
  go mod tidy
  ```
  ✅ **COMPLETED** - Core v1.2.102-0.20251224030526

- [x] **Step 5: Add DeviceSession Query Method**
  - File: `internal/repository/postgres/device_session_repository.go`
  - Method: `GetActiveByAccountID(ctx, accountID) ([]*DeviceSession, error)`
  ✅ **ALREADY EXISTS** - Repository đã có method này

- [x] **Step 6: Implement NotificationClient Methods**
  - File: `pkg/grpcclient/notification_client.go`
  - Add: `SendEventToDevices()` and `SendForceLogoutEvent()`
  ✅ **COMPLETED** - Line 275-347

- [x] **Step 7: Update SupplierUsecase**
  - File: `internal/usecase/supplier_usecase.go`
  - Add: `deviceSessionRepo` field (line 29)
  - Add: `sendForceLogoutEvent()` method (line 432)
  - Update: `DeactiveSupplier()` to call FCM (line 420)
  ✅ **COMPLETED** - All changes implemented

- [x] **Step 8: Update Dependency Injection**
  - File: `internal/api/init.go`
  - Add: `repos.DeviceSession` parameter to `NewSupplierUsecase` (line 452)
  ✅ **COMPLETED** - DI updated

- [ ] **Step 9: Test Locally**
  ```bash
  # Start noti-service
  cd noti-service
  docker-compose -f docker-compose.local.yml up -d
  
  # Start CAS
  cd centre-auth-service
  docker-compose -f docker-compose.local.yml up -d
  
  # Test integration
  ./test-fcm-integration.sh
  ```
  ⏳ **READY TO TEST**

- [ ] **Step 10: Integration Test**
  - Deactivate supplier via API
  - Check logs for FCM push
  - Verify device receives event
  ⏳ **PENDING**

- [ ] **Step 3: Generate Proto**
  ```bash
  cd Core
  make generate
  # Verify: Check gen/go/proto/notification/v1/ for new methods
  ```

- [ ] **Step 4: Update CAS Dependencies**
  ```bash
  cd centre-auth-service
  make update-core
  go mod tidy
  ```

- [ ] **Step 5: Add DeviceSession Query Method**
  - File: `internal/repository/postgres/device_session_repository.go`
  - Add: `GetActiveTokensByAccountID(ctx, accountID) ([]string, error)`

- [ ] **Step 6: Implement NotificationClient Methods**
  - File: `pkg/grpcclient/notification_client.go`
  - Add: `SendEventToDevices()` and `SendForceLogoutEvent()`

- [ ] **Step 7: Update SupplierUsecase**
  - File: `internal/usecase/supplier_usecase.go`
  - Add: `deviceSessionRepo` field
  - Add: `sendForceLogoutEvent()` method
  - Update: `DeactiveSupplier()` to call FCM

- [ ] **Step 8: Update Dependency Injection**
  - File: `internal/api/init.go`
  - Add: `repos.DeviceSession` parameter to `NewSupplierUsecase`

- [ ] **Step 9: Test Locally**
  ```bash
  # Start services
  cd noti-service && make api
  cd centre-auth-service && make api
  
  # Test gRPC
  grpcurl -plaintext localhost:9012 list api.v1.NotificationService
  ```

- [ ] **Step 10: Integration Test**
  - Deactivate supplier via API
  - Check logs for FCM push
  - Verify device receives event

---

## Summary Implementation Order

```
1. Core Proto (15 mins)
   |-- Verify/sync notification.proto
   |-- make generate
   |-- git push

2. CAS NotificationClient (30 mins)
   |-- make update-core
   |-- Add SendEventToDevices method
   |-- Add SendForceLogoutEvent helper
   |-- Implement error handling (best-effort)

3. CAS SupplierUsecase (20 mins)
   |-- Add DeviceSessionRepo dependency
   |-- Update DeactiveSupplier
   |-- Add sendForceLogoutEvent helper
   |-- Add empty token checks

4. CAS DI Update (10 mins)
   |-- Update init.go

5. Testing (30 mins)
   |-- Unit tests
   |-- Integration tests
   |-- Mobile app test

Total: ~2 hours
```

---

## Related Documents

- [noti-service/internal/api/v1/notification.proto](../noti-service/internal/api/v1/notification.proto)
- [centre-auth-service/pkg/grpcclient/notification_client.go](../centre-auth-service/pkg/grpcclient/notification_client.go)
- [centre-auth-service/internal/usecase/supplier_usecase.go](../centre-auth-service/internal/usecase/supplier_usecase.go)
- [MOBILE_APP_TESTING_GUIDE.md](./MOBILE_APP_TESTING_GUIDE.md)
