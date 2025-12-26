# Migration Plan: TOB-37 to Production Services

**Author:** Claude  
**Created:** 2025-12-23  
**Status:** Planning

---

## Overview

This document outlines the migration path from TOB-37 POC code to production services (CAS and Noti-service).

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          TOB-37 (POC)                               │
├─────────────────────────────────────────────────────────────────────┤
│  test-fcm/main.go                                                   │
│  ├── EventPayload struct                                            │
│  ├── ActionCodeRegistry                                             │
│  └── SendNotification() - Direct FCM via noti-service               │
│                                                                     │
│  demo-mobile-app/                                                   │
│  ├── eventConfig.js - Action code registry                          │
│  ├── eventHandlers.js - Generic handlers + idempotency              │
│  ├── fcmService.js - FCM initialization                             │
│  └── DebugOverlay.js - Debug UI                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Production Services                              │
├─────────────────────────────────────────────────────────────────────┤
│  centre-auth-service (CAS)                                          │
│  └── pkg/grpcclient/notification_client.go                          │
│      └── SendForceLogoutNotification() - Calls noti-service         │
│                                                                     │
│  noti-service (NS)                                                  │
│  ├── FCM credentials (fcm-dev-sdk.json)                             │
│  ├── gRPC API (SendNotification)                                    │
│  └── Actual FCM delivery                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Migration Target

### What Goes Where

| Component | Source | Target | Priority |
|-----------|--------|--------|----------|
| EventPayload struct | test-fcm/main.go | Core/proto/notification/v1/ | HIGH |
| ActionCodeRegistry | test-fcm/main.go | noti-service or CAS | MEDIUM |
| SendNotification logic | test-fcm/main.go | CAS (already partial) | HIGH |
| Mobile SDK files | demo-mobile-app/ | Real mobile app repo | HIGH |
| Documentation | TOB-37/*.md | docs/ folder | LOW |

---

## Phase 1: Proto Definition (Core Repository)

### 1.1 Create Standardized Notification Proto

**File:** `Core/proto/notification/v1/event.proto`

```protobuf
syntax = "proto3";

package api.v1;

option go_package = "dev.azure.com/agris-agriculture/Core/_git/Core.git/gen/go/proto/notification/v1;notificationv1";

// EventPayload - Standardized FCM event structure
message EventPayload {
  string version = 1;      // Schema version (e.g., "1.0")
  string action_code = 2;  // Unique event identifier
  string model = 3;        // Target model (suppliers, farmers, etc.)
  string action = 4;       // Action type (deactivate, update, etc.)
  string description = 5;  // Human-readable message
  string account_id = 6;   // Target account ID (optional)
  string timestamp = 7;    // ISO 8601 timestamp
}

// SendEventRequest - Request to send event notification
message SendEventRequest {
  string device_token = 1 [(buf.validate.field).string.min_len = 1];
  EventPayload payload = 2 [(buf.validate.field).required = true];
}

message SendEventResponse {
  bool success = 1;
  string message_id = 2;
}

// ActionCodeInfo - Registry entry for action code
message ActionCodeInfo {
  string code = 1;
  string model = 2;
  string action = 3;
  string description = 4;
}
```

### 1.2 Update NotificationService Proto

Add to existing `notification_service.proto`:

```protobuf
service NotificationService {
  // Existing
  rpc SendNotification(SendNotificationRequest) returns (SendNotificationResponse);
  
  // New - Generic event sender
  rpc SendEvent(SendEventRequest) returns (SendEventResponse);
  
  // New - Bulk event (multiple devices)
  rpc SendEventToDevices(SendEventToDevicesRequest) returns (SendEventToDevicesResponse);
}
```

---

## Phase 2: Noti-service Updates

### 2.1 Implement SendEvent Handler

**File:** `noti-service/internal/handler/event_handler.go`

```go
func (h *Handler) SendEvent(ctx context.Context, req *notiv1.SendEventRequest) (*notiv1.SendEventResponse, error) {
    // Validate action_code
    if !isValidActionCode(req.Payload.ActionCode) {
        return nil, status.Error(codes.InvalidArgument, "unknown action_code")
    }
    
    // Build FCM message
    message := &messaging.Message{
        Token: req.DeviceToken,
        Data: map[string]string{
            "version":     req.Payload.Version,
            "action_code": req.Payload.ActionCode,
            "model":       req.Payload.Model,
            "action":      req.Payload.Action,
            "description": req.Payload.Description,
            "account_id":  req.Payload.AccountId,
            "timestamp":   req.Payload.Timestamp,
        },
    }
    
    // Send via FCM
    msgID, err := h.fcmClient.Send(ctx, message)
    if err != nil {
        return nil, status.Error(codes.Internal, err.Error())
    }
    
    return &notiv1.SendEventResponse{
        Success:   true,
        MessageId: msgID,
    }, nil
}
```

### 2.2 Action Code Registry

**File:** `noti-service/internal/config/action_codes.go`

```go
package config

type ActionCodeInfo struct {
    Code        string
    Model       string
    Action      string
    Description string
}

var ActionCodes = map[string]ActionCodeInfo{
    "001": {Code: "001", Model: "suppliers", Action: "deactivate", Description: "Force logout supplier"},
    "002": {Code: "002", Model: "suppliers", Action: "update", Description: "Profile updated"},
    "003": {Code: "003", Model: "suppliers", Action: "approved", Description: "Registration approved"},
    "101": {Code: "101", Model: "farmers", Action: "deactivate", Description: "Force logout farmer"},
    "102": {Code: "102", Model: "farmers", Action: "update", Description: "Profile updated"},
    "201": {Code: "201", Model: "products", Action: "update", Description: "Product updated"},
    "202": {Code: "202", Model: "products", Action: "delete", Description: "Product deleted"},
    "301": {Code: "301", Model: "orders", Action: "created", Description: "New order received"},
    "302": {Code: "302", Model: "orders", Action: "update", Description: "Order status updated"},
}

func IsValidActionCode(code string) bool {
    _, ok := ActionCodes[code]
    return ok
}
```

---

## Phase 3: CAS Updates

### 3.1 Update Notification Client

**File:** `centre-auth-service/pkg/grpcclient/notification_client.go`

```go
// Generic SendEvent - replaces SendForceLogoutNotification
func (c *NotificationClient) SendEvent(ctx context.Context, deviceToken, actionCode, model, action, description, accountID string) error {
    req := &notiv1.SendEventRequest{
        DeviceToken: deviceToken,
        Payload: &notiv1.EventPayload{
            Version:     "1.0",
            ActionCode:  actionCode,
            Model:       model,
            Action:      action,
            Description: description,
            AccountId:   accountID,
            Timestamp:   time.Now().UTC().Format(time.RFC3339),
        },
    }
    
    _, err := c.client.SendEvent(ctx, req)
    return err
}

// Convenience methods
func (c *NotificationClient) SendForceLogout(ctx context.Context, deviceToken, accountID, userType string) error {
    actionCode := "001" // suppliers
    if userType == "farmer" {
        actionCode = "101"
    }
    
    return c.SendEvent(ctx, deviceToken, actionCode, userType+"s", "deactivate", 
        "Your account has been deactivated by administrator", accountID)
}
```

### 3.2 Update Command Handlers

Update places that call `SendForceLogoutNotification` to use new method:

```go
// Before
err := c.notiClient.SendForceLogoutNotification(ctx, deviceToken)

// After
err := c.notiClient.SendForceLogout(ctx, deviceToken, accountID, "supplier")
```

---

## Phase 4: Mobile App Migration

### 4.1 Files to Transfer

Copy from `TOB-37/demo-mobile-app/src/` to real mobile app:

| Source | Destination |
|--------|-------------|
| `config/eventConfig.js` | `src/config/eventConfig.js` |
| `handlers/eventHandlers.js` | `src/handlers/eventHandlers.js` |
| `services/fcmService.js` | `src/services/fcmService.js` |
| `components/DebugOverlay.js` | `src/components/DebugOverlay.js` (optional) |

### 4.2 Integration Steps

1. Install dependencies: `@react-native-firebase/messaging`, `@react-native-async-storage/async-storage`
2. Copy files above
3. Initialize in App.js with `registerEventCallbacks`
4. Implement actual handlers (logout, navigation, etc.)

---

## Phase 5: Documentation Migration

| Source | Destination | Action |
|--------|-------------|--------|
| `TOB-37/MASTER_GUIDE.md` | `docs/services/FCM_EVENT_SYSTEM.md` | Move & rename |
| `TOB-37/UPGRADE_GUIDE.md` | Archive or delete | Archive if needed |
| `TOB-37/demo-mobile-app/MOBILE_SDK_GUIDE.md` | `docs/mobile/FCM_INTEGRATION.md` | Move |

---

## Migration Checklist

### Pre-Migration

- [ ] Review all action codes with product team
- [ ] Confirm payload format with mobile team
- [ ] Backup TOB-37 folder

### Core Repository

- [ ] Create `notification/v1/event.proto`
- [ ] Update `notification_service.proto`
- [ ] Run `make generate`
- [ ] Tag new version

### Noti-service

- [ ] Update Core dependency
- [ ] Implement `SendEvent` handler
- [ ] Add action code registry
- [ ] Add unit tests
- [ ] Deploy to staging

### CAS

- [ ] Update Core dependency
- [ ] Update notification client
- [ ] Update command handlers
- [ ] Add unit tests
- [ ] Deploy to staging

### Mobile App

- [ ] Copy SDK files
- [ ] Install dependencies
- [ ] Integrate with existing auth flow
- [ ] Test all action codes
- [ ] Deploy to TestFlight/Play Store internal

### Post-Migration

- [ ] End-to-end testing
- [ ] Move documentation
- [ ] Delete TOB-37 folder
- [ ] Update related tickets

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Proto | 1 day | None |
| Phase 2: Noti-service | 2 days | Phase 1 |
| Phase 3: CAS | 1 day | Phase 1, 2 |
| Phase 4: Mobile | 3 days | Phase 2, 3 |
| Phase 5: Docs | 0.5 day | All phases |
| Testing | 2 days | All phases |

**Total:** ~1.5 weeks

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing FCM | HIGH | Deploy noti-service with backward compat |
| Mobile app rejection | MEDIUM | Thorough testing on staging |
| Action code conflicts | LOW | Centralized registry in noti-service |

