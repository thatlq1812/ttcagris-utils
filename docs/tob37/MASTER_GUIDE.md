# TOB-37: FCM Force Logout - Implementation Guide

**Author:** Le Quang That  
**Created:** December 22, 2025  
**Last Updated:** December 23, 2025  
**Status:** COMPLETED  
**Jira Ticket:** TOB-37 - [Training] Send event action to mobile app

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Payload Format](#payload-format)
4. [Backend Implementation](#backend-implementation)
5. [Mobile App Integration](#mobile-app-integration)
6. [Testing Guide](#testing-guide)
7. [Files Reference](#files-reference)
8. [Extending for Other Actions](#extending-for-other-actions)

---

## Overview

### Business Requirement

When a supplier account is deactivated in Centre Auth Service (CAS):
1. Backend sends FCM notification to all registered devices
2. Mobile app receives notification with action payload
3. App clears authentication tokens and redirects to login screen

### Technical Approach

- **Transport**: Firebase Cloud Messaging (FCM)
- **Backend**: CAS -> Noti-service -> FCM
- **Mobile**: React Native with @react-native-firebase/messaging
- **No WebSocket**: One-way push, no persistent connection

---

## Architecture

### Flow Diagram

```
+-----------------+
|  Admin Portal   |
|  (Gateway API)  |
+--------+--------+
         | POST /api/v1/suppliers/{id}/deactivate
         v
+-----------------+
|      CAS        |
|  (port 50051)   |
|                 |
| DeactivateSupplier|
|       |         |
| SendForceLogout |
|   Notification  |
+--------+--------+
         | gRPC: SendNotificationToUser
         v
+-----------------+
|  Noti-Service   |
|  (port 9013)    |
|                 |
| GetDeviceTokens |<--- gRPC call to CAS.DeviceService
|       |         |
| SendToFCM       |
+--------+--------+
         | FCM API
         v
+-----------------+
|    Firebase     |
|      FCM        |
+--------+--------+
         | Push Notification
         v
+-----------------+
|   Mobile App    |
|                 |
| handleMessage() |
|       |         |
| Force Logout    |
+-----------------+
```

### Service Ports

| Service | gRPC Port | HTTP Port |
|---------|-----------|-----------|
| CAS (centre-auth-service) | 50051 | 4000 |
| Noti-service | 9013 | 8000 |

---

## Payload Format

### Standardized FCM Data Payload

```json
{
  "version": "1.0",
  "action_code": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Your supplier account has been deactivated",
  "account_id": "12345",
  "timestamp": "2025-12-23T10:00:00Z",
  "type": "FORCE_LOGOUT"
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Payload schema version (e.g., "1.0") |
| `action_code` | string | Unique action identifier (e.g., "001" = deactivate supplier) |
| `model` | string | Target model: `suppliers`, `farmers`, `products` |
| `action` | string | Action type: `deactivate`, `update`, `delete`, `create` |
| `description` | string | Human-readable description |
| `account_id` | string | Target account ID |
| `timestamp` | string | ISO 8601 timestamp |
| `type` | string | Legacy field for backward compatibility |

### Action Codes

| Code | Model | Action | Description |
|------|-------|--------|-------------|
| 001 | suppliers | deactivate | Deactivate supplier - Force logout |
| 002 | suppliers | update | Supplier data updated |
| 003 | suppliers | delete | Supplier deleted |
| 101 | farmers | deactivate | Deactivate farmer |
| 201 | products | update | Product updated |

---

## Backend Implementation

### 1. CAS - SendForceLogoutNotification

**File:** `centre-auth-service/pkg/grpcclient/notification_client.go`

```go
func (c *NotificationClient) SendForceLogoutNotification(
    ctx context.Context,
    accountID int64,
    reason string,
) (*notificationv1.BaseResponse, error) {
    req := &notificationv1.SendNotificationRequest{
        AccountId:   fmt.Sprintf("%d", accountID),
        TargetApps:  []string{"supplier_app"},
        TargetRoles: []string{"supplier"},
        Title:       "Account Deactivated",
        Body:        reason,
        Type:        &forceLogoutType,
        Priority:    &highPriority,
        Action: &notificationv1.NotificationAction{
            Type: "FORCE_LOGOUT",
            Payload: map[string]string{
                "version":     "1.0",
                "action_code": "001",
                "model":       "suppliers",
                "action":      "deactivate",
                "description": reason,
                "account_id":  accountIDStr,
            },
        },
    }
    return c.notificationClient.SendNotificationToUser(ctx, req)
}
```

### 2. CAS - DeactivateSupplier Usecase

**File:** `centre-auth-service/internal/usecase/supplier_usecase.go`

```go
func (uc *supplierUsecase) DeactivateSupplier(ctx context.Context, supplierID int64) (bool, error) {
    // ... toggle is_active_supplier logic ...

    // Send force logout notification when supplier is deactivated
    if !newIsActiveSupplier {
        if uc.notificationClient != nil {
            reason := "Your supplier account has been deactivated."
            _, err := uc.notificationClient.SendForceLogoutNotification(ctx, accountID, reason)
            if err != nil {
                uc.logger.Warn("Failed to send force logout notification", zap.Error(err))
                // Don't fail - deactivation already succeeded
            }
        }
    }
    return newIsActiveSupplier, nil
}
```

### 3. Noti-service - BuildNotificationData

**File:** `noti-service/internal/domain/models/notification.go`

```go
func (n Notification) BuildNotificationData() map[string]string {
    data := make(map[string]string)
    data["type"] = n.Type
    data["category"] = n.Category
    data["source"] = n.Source

    if n.Action != nil {
        data["action_type"] = n.Action.Type
        // Pass payload fields directly (no prefix)
        for key, value := range n.Action.Payload {
            data[key] = value
        }
    }
    return data
}
```

### 4. Configuration

**CAS config.yaml:**
```yaml
services:
  notification: "localhost:9013"  # Noti-service gRPC port
```

**Noti-service config.yml:**
```yaml
adapter:
  grpc:
    cas-service: "localhost:50051"  # CAS gRPC port

firebase:
  credentialFilePath: ./fcm-dev-sdk.json
```

---

## Mobile App Integration

### 1. Dependencies

```json
{
  "@react-native-firebase/app": "^21.6.1",
  "@react-native-firebase/messaging": "^21.6.1",
  "@react-native-async-storage/async-storage": "^2.1.0"
}
```

### 2. FCM Service

**File:** `demo-mobile-app/src/services/fcmService.js`

```javascript
// Action codes from backend
const ACTION_CODES = {
  DEACTIVATE_SUPPLIER: '001',
  UPDATE_SUPPLIER: '002',
  DELETE_SUPPLIER: '003',
};

const MODELS = {
  SUPPLIERS: 'suppliers',
  FARMERS: 'farmers',
  PRODUCTS: 'products',
};

class FCMService {
  async handleMessage(remoteMessage, source) {
    const data = remoteMessage.data || {};
    const actionCode = data.action_code;
    const model = data.model;
    const action = data.action;

    if (actionCode) {
      await this.handleByActionCode(actionCode, model, action, data);
    }
  }

  async handleByActionCode(actionCode, model, action, data) {
    switch (actionCode) {
      case ACTION_CODES.DEACTIVATE_SUPPLIER:
        if (model === MODELS.SUPPLIERS && action === 'deactivate') {
          await this.handleForceLogout(data);
        }
        break;
      // Add more cases as needed
    }
  }

  async handleForceLogout(data) {
    // Clear auth tokens
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.AUTH_TOKEN,
      STORAGE_KEYS.USER_DATA,
    ]);
    
    // Trigger callback to navigate to login
    if (this.onForceLogoutCallback) {
      this.onForceLogoutCallback({
        reason: data.description,
      });
    }
  }
}
```

### 3. Background Handler

**File:** `demo-mobile-app/index.js`

```javascript
import messaging from '@react-native-firebase/messaging';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Must be registered at top level (outside component)
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  const data = remoteMessage.data || {};
  
  if (data.action_code === '001' && data.action === 'deactivate') {
    // Clear auth in background
    await AsyncStorage.multiRemove(['@auth_token', '@user_data']);
  }
});
```

### 4. App.js Integration

```javascript
import { fcmService } from './src/services/fcmService';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [forceLogoutData, setForceLogoutData] = useState(null);

  useEffect(() => {
    // Set force logout callback
    fcmService.setForceLogoutCallback((data) => {
      setForceLogoutData(data);
      setIsLoggedIn(false);
    });

    fcmService.initialize();
  }, []);

  return (
    <>
      {isLoggedIn ? <HomeScreen /> : <LoginScreen />}
      <ForceLogoutModal
        visible={!!forceLogoutData}
        data={forceLogoutData}
        onDismiss={() => setForceLogoutData(null)}
      />
    </>
  );
}
```

---

## Testing Guide

### Prerequisites

1. **FCM Credentials**: `noti-service/fcm-dev-sdk.json`
2. **Mobile App**: Running on physical device (emulator FCM may not work)
3. **Get FCM Token**: From app's login screen

### Option 1: Direct FCM Test (No Database Required)

```bash
cd TOB-37/test-fcm

# Force logout (default action code 001)
go run main.go -token "YOUR_FCM_TOKEN"

# With custom description
go run main.go -token "YOUR_FCM_TOKEN" -desc "Test force logout"

# Other events (using action code registry)
go run main.go -token "YOUR_FCM_TOKEN" -code 002  # Supplier update
go run main.go -token "YOUR_FCM_TOKEN" -code 003  # Supplier approved
```

**Expected Output:**
```
=== FCM Event Test Script ===
Action Code: 001
Model: suppliers
Action: deactivate
Payload: {"version":"1.0","action_code":"001","model":"suppliers",...}
Sending FCM message...
=== SUCCESS ===
Message ID: projects/agrios-notification-demo/messages/xxx
```

### Option 2: Full Flow Test (Requires Services)

1. **Start Services:**
```bash
# Terminal 1: CAS
cd centre-auth-service && make api

# Terminal 2: Noti-service  
cd noti-service && make api
```

2. **Register Device Token:**
```bash
grpcurl -plaintext -d '{
  "account_id": 12345,
  "firebase_token": "YOUR_FCM_TOKEN",
  "device_id": "test-device-001"
}' localhost:50051 device.v1.DeviceService/RegisterDevice
```

3. **Call DeactivateSupplier:**
```bash
grpcurl -plaintext -d '{"id": 1}' \
  localhost:50051 supplier.v1.SupplierService/DeactivateSupplier
```

4. **Expected Result:**
- Mobile app receives FCM notification
- Force Logout modal appears
- App navigates to login screen

---

## Files Reference

### TOB-37 Directory Structure

```
TOB-37/
├── MASTER_GUIDE.md          # This document
├── UPGRADE_GUIDE.md         # Architecture details
├── docker-compose.yml       # Database setup
├── init-databases.sql       # SQL initialization
├── demo-mobile-app/         # Mobile app template
│   ├── src/
│   │   ├── components/
│   │   │   ├── ForceLogoutModal.js
│   │   │   ├── DebugOverlay.js    # Debug panel (dev only)
│   │   │   └── index.js
│   │   ├── config/
│   │   │   └── eventConfig.js     # Action code registry
│   │   ├── handlers/
│   │   │   └── eventHandlers.js   # Generic handlers + idempotency
│   │   ├── screens/
│   │   │   ├── LoginScreen.js
│   │   │   └── HomeScreen.js
│   │   └── services/
│   │       ├── fcmService.js      # Config-driven FCM handler
│   │       └── apiService.js
│   ├── App.js                     # Event callbacks registration
│   ├── index.js
│   └── README.md
└── test-fcm/                # FCM test script
    ├── main.go              # Generic EventPayload + CLI
    ├── go.mod
    └── go.sum
```

### Backend Files Modified

| Service | File | Purpose |
|---------|------|---------|
| CAS | `pkg/grpcclient/notification_client.go` | SendForceLogoutNotification method |
| CAS | `internal/usecase/supplier_usecase.go` | Call notification on deactivate |
| CAS | `config/config.yaml` | Notification service port (9013) |
| Noti | `internal/domain/models/notification.go` | BuildNotificationData - payload format |
| Noti | `config/config.yml` | CAS service port (50051) |

---

## Extending for Other Actions

### Adding New Action Code

1. **CAS - Add new method:**
```go
// pkg/grpcclient/notification_client.go
func (c *NotificationClient) SendSupplierUpdateNotification(
    ctx context.Context,
    accountID int64,
    updateInfo string,
) (*notificationv1.BaseResponse, error) {
    req := &notificationv1.SendNotificationRequest{
        // ...
        Action: &notificationv1.NotificationAction{
            Type: "UPDATE",
            Payload: map[string]string{
                "action_code": "002",
                "model":       "suppliers",
                "action":      "update",
                "description": updateInfo,
            },
        },
    }
    // ...
}
```

2. **Mobile - Add handler:**
```javascript
// src/services/fcmService.js
case ACTION_CODES.UPDATE_SUPPLIER:
  console.log('Supplier updated:', data.description);
  // Refresh supplier data
  if (this.onDataRefreshCallback) {
    this.onDataRefreshCallback('suppliers');
  }
  break;
```

### Action Code Convention

```
Format: XYY
  X   = Model category (0=suppliers, 1=farmers, 2=products, ...)
  YY  = Action sequence (01=deactivate, 02=update, 03=delete, ...)

Examples:
  001 = Supplier Deactivate
  002 = Supplier Update
  101 = Farmer Deactivate
  201 = Product Update
```

---

## Troubleshooting

### FCM Token Invalid

**Error:** `The registration token is not a valid FCM registration token`

**Solution:**
- Ensure token is from physical device (not emulator)
- Token must be fresh (regenerate if app was reinstalled)
- Check google-services.json matches Firebase project

### Notification Not Received

**Checklist:**
1. App has notification permission
2. FCM token registered correctly
3. Device has internet connection
4. Check Firebase Console for delivery status

### Services Cannot Connect

**CAS -> Noti-service:**
- Verify `config.yaml` has correct port: `notification: "localhost:9013"`

**Noti-service -> CAS:**
- Verify `config.yml` has correct port: `cas-service: "localhost:50051"`

---

## Summary

This implementation enables real-time event pushing from backend to mobile app using FCM, with a standardized payload format that supports multiple action types. The architecture is extensible for future use cases beyond force logout.

**Key Benefits:**
- No WebSocket required (cost-effective)
- Works when app is in background/killed
- Standardized payload for multiple action types
- Config-driven event handling (no code changes for new events)
- Idempotency (duplicate prevention)
- Backward compatible with legacy format

**What's Completed:**
- [x] Payload format with version, action_code, model, action, description
- [x] Backend: CAS -> Noti-service -> FCM flow
- [x] Mobile: FCM handler with action code routing
- [x] Mobile: Debug Overlay for viewing FCM logs/payload
- [x] Mobile: Config-driven event handlers (`eventConfig.js` + `eventHandlers.js`)
- [x] Mobile: Idempotency handling (60s TTL deduplication)
- [x] Test script: Generic EventPayload with CLI flags
- [x] Documentation: MASTER_GUIDE.md + UPGRADE_GUIDE.md

**See Also:** [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) for architecture details
