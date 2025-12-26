# TOB-37: Event Action System - Upgrade Guide

**Author:** Le Quang That  
**Created:** December 23, 2025  
**Purpose:** Refactor from Force Logout specific to Generic Event System

---

## Problem Statement

### Current State (Force Logout Specific)
```
ForceLogoutPayload
SendForceLogoutNotification()
handleForceLogout()
```

### Target State (Generic Event System)
```
EventPayload
SendEventNotification(eventType, model, action, ...)
handleEvent()
```

---

## Design Philosophy

### 1. Payload as Contract

Mobile app should be able to handle ANY event based on payload, not hardcoded handlers.

```json
{
  "version": "1.0",
  "action_code": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Human readable message",
  "data": {
    "account_id": "12345",
    "extra_field": "value"
  }
}
```

### 2. Action Code Registry

Central registry of all action codes (can be in docs or config):

| Code | Model | Action | Mobile Behavior |
|------|-------|--------|-----------------|
| 001 | suppliers | deactivate | Force logout |
| 002 | suppliers | update | Refresh data |
| 003 | suppliers | approved | Show toast + navigate |
| 101 | farmers | deactivate | Force logout |
| 102 | farmers | update | Refresh data |
| 201 | products | update | Refresh product list |
| 202 | products | delete | Remove from local cache |

### 3. Mobile App Decision Tree

```
Receive FCM
    |
    v
Parse action_code + model + action
    |
    v
Lookup behavior in config/handler
    |
    +---> "logout" -> Clear auth, navigate to login
    +---> "refresh" -> Reload data from API
    +---> "navigate" -> Go to specific screen
    +---> "toast" -> Show notification message
    +---> "modal" -> Show modal dialog
```

### 4. Versioning Strategy

Payload includes `version` field for future compatibility:

```javascript
// Mobile version check
const handlePayload = (payload) => {
  const version = payload.version || "1.0";
  
  if (version !== SUPPORTED_VERSION) {
    console.warn(`Unsupported payload version: ${version}`);
    // Graceful fallback - try to handle anyway
  }
  
  processEvent(payload);
};
```

**Version Policy:**
- Minor changes (add optional field): Keep same version
- Breaking changes (rename/remove field): Bump version
- Mobile app should handle unknown versions gracefully

### 5. Idempotency Handling

Firebase may deliver same notification multiple times. Mobile must handle duplicates:

```javascript
// Store processed event IDs (with TTL)
const PROCESSED_EVENTS = new Map();
const EVENT_TTL_MS = 60000; // 1 minute

const handleEvent = async (payload) => {
  const eventKey = `${payload.action_code}_${payload.timestamp}`;
  
  // Check if already processed
  if (PROCESSED_EVENTS.has(eventKey)) {
    console.log('Duplicate event ignored:', eventKey);
    return;
  }
  
  // Mark as processed
  PROCESSED_EVENTS.set(eventKey, Date.now());
  
  // Clean old entries
  cleanExpiredEvents();
  
  // Process event
  await processEvent(payload);
};

const cleanExpiredEvents = () => {
  const now = Date.now();
  for (const [key, timestamp] of PROCESSED_EVENTS.entries()) {
    if (now - timestamp > EVENT_TTL_MS) {
      PROCESSED_EVENTS.delete(key);
    }
  }
};
```

**Idempotency Rules:**
- Use `action_code + timestamp` as unique event key
- Cache processed events for 60 seconds (configurable)
- For logout: Check if already logged out before clearing again

---

## Refactoring Plan

### Phase 1: Backend - Generic Event Sender

**1.1 CAS - notification_client.go**

FROM:
```go
func SendForceLogoutNotification(accountID int64, reason string)
```

TO:
```go
// Generic event sender
func SendEventNotification(ctx context.Context, params EventParams) error

type EventParams struct {
    AccountID   int64
    ActionCode  string  // "001", "002", etc.
    Model       string  // "suppliers", "farmers", etc.
    Action      string  // "deactivate", "update", etc.
    Description string  // Human readable
    Data        map[string]string // Extra data
}
```

**1.2 Usage in Usecase**

```go
// DeactivateSupplier usecase
uc.notificationClient.SendEventNotification(ctx, EventParams{
    AccountID:   accountID,
    ActionCode:  "001",
    Model:       "suppliers",
    Action:      "deactivate",
    Description: "Your supplier account has been deactivated",
})

// ApproveSupplier usecase  
uc.notificationClient.SendEventNotification(ctx, EventParams{
    AccountID:   accountID,
    ActionCode:  "003",
    Model:       "suppliers",
    Action:      "approved",
    Description: "Your supplier registration has been approved!",
})
```

### Phase 2: Test Script - Generic [DONE]

**2.1 test-fcm/main.go**

Implemented with:
- `EventPayload` struct with version field
- `ActionCodeRegistry` for preset action codes
- CLI flags: `-token`, `-code`, `-model`, `-action`, `-desc`, `-title`
- Auto-fill from action code registry

**2.2 CLI Usage**

```bash
# Force logout
go run main.go -code 001 -model suppliers -action deactivate -desc "Account deactivated"

# Supplier approved
go run main.go -code 003 -model suppliers -action approved -desc "Registration approved"

# Product update
go run main.go -code 201 -model products -action update -desc "Product price changed"
```

### Phase 3: Mobile App - Debug + Generic Handler

**3.1 Add Debug Overlay**

Show raw payload on screen for development:

```javascript
// DebugOverlay.js
const DebugOverlay = ({ lastPayload }) => {
  if (!__DEV__) return null;
  
  return (
    <View style={styles.debugOverlay}>
      <Text style={styles.debugTitle}>Last FCM Payload:</Text>
      <Text style={styles.debugJson}>
        {JSON.stringify(lastPayload, null, 2)}
      </Text>
    </View>
  );
};
```

**3.2 Generic Event Handler**

```javascript
// eventHandlers.js
const EVENT_BEHAVIORS = {
  // Format: "action_code" -> behavior
  "001": { type: "logout", message: "Account deactivated" },
  "002": { type: "refresh", target: "supplier_profile" },
  "003": { type: "navigate", screen: "SupplierApproved" },
  "101": { type: "logout", message: "Account deactivated" },
  "201": { type: "refresh", target: "products" },
};

const handleEvent = async (payload) => {
  const behavior = EVENT_BEHAVIORS[payload.action_code];
  
  if (!behavior) {
    console.warn('Unknown action_code:', payload.action_code);
    return;
  }
  
  switch (behavior.type) {
    case 'logout':
      await clearAuth();
      navigateToLogin();
      break;
    case 'refresh':
      await refreshData(behavior.target);
      break;
    case 'navigate':
      navigateTo(behavior.screen, payload.data);
      break;
  }
};
```

**3.3 Config-Driven (Advanced)**

```javascript
// Can be fetched from backend or bundled
const EVENT_CONFIG = {
  "001": {
    behavior: "logout",
    showModal: true,
    modalTitle: "Session Ended",
  },
  "002": {
    behavior: "refresh",
    refreshTargets: ["profile", "settings"],
  },
};
```

---

## File Changes Summary

### Files Refactored

| File | Change |
|------|--------|
| `test-fcm/main.go` | `ForceLogoutPayload` -> `EventPayload`, add CLI flags |
| `demo-mobile-app/src/services/fcmService.js` | Config-driven handler, imports eventHandlers |
| `demo-mobile-app/App.js` | DebugOverlay + registerEventCallbacks |

### New Files Created

| File | Purpose |
|------|---------|
| `demo-mobile-app/src/config/eventConfig.js` | Action code -> behavior mapping (8 events) |
| `demo-mobile-app/src/components/DebugOverlay.js` | Show raw payload + logs |
| `demo-mobile-app/src/handlers/eventHandlers.js` | Generic handlers + idempotency |

---

## Testing Strategy

### 1. Mobile App Debug Mode

App shows raw payload overlay:
```
+---------------------------+
|  [DEBUG] Last Payload     |
|  {                        |
|    "version": "1.0",      |
|    "action_code": "001",  |
|    "model": "suppliers",  |
|    "action": "deactivate",|
|    ...                    |
|  }                        |
+---------------------------+
|                           |
|   [ Main App Content ]    |
|                           |
+---------------------------+
```

### 2. Test Different Events

```bash
# Test each action code
go run main.go -token $TOKEN -code 001 -model suppliers -action deactivate
go run main.go -token $TOKEN -code 002 -model suppliers -action update
go run main.go -token $TOKEN -code 003 -model suppliers -action approved
```

### 3. Verify Mobile Behavior

| Action Code | Expected Behavior |
|-------------|-------------------|
| 001 | Logout + modal |
| 002 | Refresh data + toast |
| 003 | Navigate to approved screen |

---

## Implementation Checklist

### Phase 1: Refactor Naming (Backend) [DONE]
- [x] Rename `ForceLogoutPayload` to `EventPayload` in test-fcm
- [x] Add generic flags to test script (-code, -model, -action)
- [x] Add version field to payload
- [ ] Add `SendEventNotification()` to CAS notification client (optional - current wrapper works)

### Phase 2: Mobile Debug Mode [DONE]
- [x] Create DebugOverlay component (`src/components/DebugOverlay.js`)
- [x] Store last received payload in fcmService
- [x] Display raw JSON in dev mode with tabs (Payload/Logs)
- [x] Add "Copy Payload" button
- [x] Integrate into App.js with state management

### Phase 3: Generic Handler [DONE]
- [x] Create eventConfig.js with action code mapping
- [x] Create eventHandlers.js with behavior implementations
- [x] Refactor fcmService to use config-driven approach
- [x] Add idempotency handling (deduplicate events)

### Phase 4: Documentation [DONE]
- [x] Update MASTER_GUIDE with generic approach
- [x] Document all action codes in registry
- [x] Add versioning and idempotency notes

---

## Quick Start for Adding New Event

### Step 1: Define Action Code

Add to registry (MASTER_GUIDE.md):
```
| 301 | orders | created | New order notification |
```

### Step 2: Backend - Add Call

```go
// In order creation usecase
notificationClient.SendEventNotification(ctx, EventParams{
    ActionCode:  "301",
    Model:       "orders",
    Action:      "created",
    Description: "You have a new order!",
    Data: map[string]string{
        "order_id": orderID,
    },
})
```

### Step 3: Mobile - Add Config

```javascript
// eventConfig.js
"301": {
  behavior: "navigate",
  screen: "OrderDetails",
  showToast: true,
  toastMessage: "New order received!",
}
```

Done! No code changes needed in handlers.

---

## Next Steps

### All Phases Complete

The generic event system is now fully implemented:

1. **Backend**: Test script with generic EventPayload
2. **Mobile Debug**: DebugOverlay with logs/payload tabs
3. **Config-driven**: eventConfig.js + eventHandlers.js
4. **Idempotency**: 60-second TTL for duplicate prevention

### Optional Future Enhancements

1. **Backend generic method**: Add `SendEventNotification()` wrapper in CAS
2. **API config sync**: Fetch action codes from backend on app start
3. **Custom handlers**: Add `BEHAVIORS.CUSTOM` with function references
4. **Persistent idempotency**: Store processed events in AsyncStorage
