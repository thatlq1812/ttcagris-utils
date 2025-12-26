# TOB-37: FCM Event Action System - Implementation Guide

**Author:** Le Quang That  
**Created:** December 23, 2025  
**Last Updated:** December 23, 2025  
**Status:** Completed  
**Jira Ticket:** TOB-37 - [Training] Send event action to mobile app

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Payload Format](#payload-format)
4. [Action Code Registry](#action-code-registry)
5. [gRPC API Reference](#grpc-api-reference)
6. [Implementation Details](#implementation-details)
7. [Testing Guide](#testing-guide)
8. [Docker Setup](#docker-setup)
9. [Mobile App Integration](#mobile-app-integration)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### Business Requirement

Send event actions from backend services to mobile app via Firebase Cloud Messaging (FCM). Primary use case: Force logout when supplier/farmer account is deactivated.

### Technical Approach

- **Transport**: Firebase Cloud Messaging (FCM) - Data-only messages
- **Protocol**: gRPC for inter-service communication
- **No WebSocket**: One-way push, no persistent connection needed
- **Near real-time**: FCM provides sub-second delivery

### What Was Implemented

| Component | Description |
|-----------|-------------|
| `SendEventToDevices` | Core RPC - Send structured event to device tokens |
| `SendNotificationToDevices` | Send standard notification to devices |
| `SendNotificationToTopic` | Send notification to FCM topic |
| `event_registry.go` | Action code constants for reference |

---

## Quick Start

For first-time setup, follow these steps:

### Prerequisites Checklist

- [ ] Go 1.25+ installed
- [ ] Docker Desktop running
- [ ] grpcurl installed
- [ ] Firebase project created
- [ ] FCM service account key downloaded

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://YOUR_PAT@dev.azure.com/agris-agriculture/AgriOS/_git/noti-service
cd noti-service

# 2. Place FCM key file
# Download from Firebase Console → Project Settings → Service accounts
cp ~/Downloads/your-firebase-adminsdk-key.json config/fcm-dev-sdk.json

# 3. Build Linux binary
export CGO_ENABLED=0 GOOS=linux GOARCH=amd64
go build -o bin/noti-service-linux ./cmd/main.go

# 4. Start Docker services
cd test
docker-compose -f docker-compose.test.yml up -d

# 5. Wait for services to start
sleep 15

# 6. Verify gRPC is working
grpcurl -plaintext localhost:9012 list

# 7. Send test notification (replace with your FCM token)
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN"],
  "actionCode": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Test force logout"
}' localhost:9012 api.v1.NotificationService/SendEventToDevices
```

### Get FCM Token from Mobile App

1. Install demo app: `TOB-37/demo-mobile-app/android/app/build/outputs/apk/debug/app-debug.apk`
2. Open app, tap **Quick Login (Demo)**
3. On Home screen, tap **Copy Token**
4. Use copied token in grpcurl command above

---

## Architecture

### Service Flow

```
┌─────────────────┐     gRPC      ┌──────────────────┐     FCM      ┌─────────────┐
│   CAS Service   │ ─────────────>│   Noti-Service   │ ────────────>│ Mobile App  │
│  (port 50051)   │               │   (port 9012)    │              │             │
└─────────────────┘               └──────────────────┘              └─────────────┘
                                         │
                                         v
                                  ┌──────────────┐
                                  │   Firebase   │
                                  │     FCM      │
                                  └──────────────┘
```

### Service Ports

| Service | gRPC Port | HTTP Port |
|---------|-----------|-----------|
| Noti-service | 9012 | 8000 |
| CAS (future) | 50051 | 4000 |

---

## Payload Format

### FCM Data Payload Structure

Mobile app receives this JSON in FCM data message:

```json
{
  "action_code": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Your supplier account has been deactivated"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `action_code` | string | Yes | Unique action identifier (e.g., "001") |
| `model` | string | Yes | Target model: `suppliers`, `farmers`, `products` |
| `action` | string | Yes | Action type: `deactivate`, `update`, `delete` |
| `description` | string | No | Human-readable message |

**Note:** Fields `title`, `accountId`, `type` were removed per mentor feedback to keep payload minimal.

---

## Action Code Registry

### Force Logout Events (001-010)

| Code | Model | Action | Description | Mobile Behavior |
|------|-------|--------|-------------|-----------------|
| 001 | suppliers | deactivate | Supplier deactivated | Force logout |
| 002 | buyers | deactivate | Buyer deactivated | Force logout |
| 003 | suppliers | suspend | Supplier suspended | Force logout |
| 004 | buyers | suspend | Buyer suspended | Force logout |
| 005 | users | password_changed | Password changed | Force logout |
| 006 | users | session_revoked | Session revoked | Force logout |

### Account Events (100-199)

| Code | Model | Action | Description | Mobile Behavior |
|------|-------|--------|-------------|-----------------|
| 101 | suppliers | approved | Registration approved | Toast + Navigate |
| 102 | suppliers | rejected | Registration rejected | Toast |
| 103 | buyers | approved | Buyer approved | Toast + Navigate |

### Order Events (200-299)

| Code | Model | Action | Description | Mobile Behavior |
|------|-------|--------|-------------|-----------------|
| 201 | orders | created | New order | Refresh list |
| 202 | orders | status_changed | Status updated | Refresh detail |

---

## gRPC API Reference

### Service Definition

```protobuf
service NotificationService {
  // Existing methods
  rpc SendNotificationToUser(SendNotificationRequest) returns (BaseResponse) {}
  rpc SendNotificationToUserByTemplate(SendNotificationToUserByTemplateRequest) returns (BaseResponse) {}

  // FCM
  rpc SendEventToDevices(SendEventToDevicesRequest) returns (BaseResponse) {}
  rpc SendNotificationToDevices(SendNotificationToDevicesRequest) returns (BaseResponse) {}
  rpc SendNotificationToTopic(SendNotificationToTopicRequest) returns (BaseResponse) {}

  // EndUser APIs
  rpc GetNotifications(GetNotificationsRequest) returns (GetNotificationsResponse) {}
  rpc GetUnreadCount(GetUnreadCountRequest) returns (GetUnreadCountResponse) {}
  rpc MarkAsReadNotification(MarkAsReadNotificationRequest) returns (google.protobuf.Empty) {}
  rpc ClearNotifications(ClearNotificationsRequest) returns (google.protobuf.Empty) {}
}
```

### SendEventToDevices Request

```protobuf
message SendEventToDevicesRequest {
  repeated string device_tokens = 1;  // FCM device tokens (required, min 1)
  string action_code = 2;             // e.g., "001" (required)
  string model = 3;                   // e.g., "suppliers" (required)
  string action = 4;                  // e.g., "deactivate" (required)
  string description = 5;             // Human-readable message
  map<string, string> data = 6;       // Additional custom data
}
```

### BaseResponse

```protobuf
message BaseResponse {
  int32 success_count = 1;
  int32 failure_count = 2;
  repeated string failed_tokens = 3;
}
```

---

## Configuration Setup

### 1. Firebase Cloud Messaging (FCM) Credentials

#### Get FCM Service Account Key

1. **Access Firebase Console:**
   - Go to [https://console.firebase.google.com](https://console.firebase.google.com)
   - Select your project (e.g., `agrios-notification-demo`)

2. **Navigate to Service Accounts:**
   ```
   Project Settings () → Service accounts → Firebase Admin SDK
   ```

3. **Generate Private Key:**
   - Click **Generate new private key**
   - Click **Generate key** to confirm
   - JSON file will be downloaded automatically (e.g., `agrios-notification-demo-firebase-adminsdk-xxxxx.json`)

4. **Place in Project:**
   ```bash
   # Move downloaded file to noti-service config folder
   mv ~/Downloads/agrios-notification-demo-firebase-adminsdk-xxxxx.json noti-service/config/fcm-dev-sdk.json
   
   # Or rename existing file
   cd noti-service/config
   mv agrios-notification-demo-firebase-adminsdk-fbsvc-57ec29e0f2.json fcm-dev-sdk.json
   ```

5. **Verify File Structure:**
   ```json
   {
     "type": "service_account",
     "project_id": "agrios-notification-demo",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "firebase-adminsdk-xxxxx@agrios-notification-demo.iam.gserviceaccount.com",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "..."
   }
   ```

**Security Note:** Never commit this file to Git. Already in `.gitignore`:
```gitignore
# Firebase credentials
fcm-*.json
*-firebase-adminsdk-*.json
```

### 2. Application Configuration

#### config.yaml Structure

```yaml
server:
  env: development
  grpc_port: 9012        # gRPC server port
  http_port: 8000        # HTTP/Fiber server port
  log_level: debug       # debug, info, warn, error

firebase:
  credentials_path: config/fcm-dev-sdk.json  # Path to FCM key
  project_id: agrios-notification-demo        # Firebase project ID

database:
  host: localhost        # Docker: postgres
  port: 5432            # Docker: Use internal port
  username: postgres
  password: postgres
  database: noti_db
  ssl_mode: disable
  max_open_conns: 25
  max_idle_conns: 5
  conn_max_lifetime: 5m

redis:
  host: localhost       # Docker: redis
  port: 6379
  password: ""
  db: 0
  pool_size: 10

logging:
  level: debug
  format: json          # json or console
  output: stdout        # stdout or file path
```

#### Environment Variables Override

You can override config values with environment variables:

```bash
# Server
export SERVER_GRPC_PORT=9012
export SERVER_HTTP_PORT=8000

# Firebase
export FIREBASE_CREDENTIALS_PATH=config/fcm-dev-sdk.json
export FIREBASE_PROJECT_ID=agrios-notification-demo

# Database
export DATABASE_HOST=postgres
export DATABASE_PORT=5432
export DATABASE_USERNAME=postgres
export DATABASE_PASSWORD=postgres
export DATABASE_NAME=noti_db

# Redis
export REDIS_HOST=redis
export REDIS_PORT=6379
```

### 3. Docker Configuration Files

#### test/docker-compose.test.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:17-alpine
    container_name: noti-service-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: noti_db
    ports:
      - "5433:5432"  # External:Internal (avoid conflict with local postgres)
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ../migrations:/docker-entrypoint-initdb.d  # Auto-run migrations
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: noti-service-redis
    ports:
      - "6380:6379"  # External:Internal
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  noti-service:
    build:
      context: ..
      dockerfile: test/Dockerfile.test
    container_name: noti-service-app
    ports:
      - "8000:8000"   # HTTP/Fiber
      - "9012:9012"   # gRPC
    environment:
      # Server
      SERVER_ENV: development
      SERVER_GRPC_PORT: 9012
      SERVER_HTTP_PORT: 8000
      
      # Database (use service name as host)
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_USERNAME: postgres
      DATABASE_PASSWORD: postgres
      DATABASE_NAME: noti_db
      DATABASE_SSL_MODE: disable
      
      # Redis (use service name as host)
      REDIS_HOST: redis
      REDIS_PORT: 6379
      
      # Firebase
      FIREBASE_CREDENTIALS_PATH: config/fcm-dev-sdk.json
      FIREBASE_PROJECT_ID: agrios-notification-demo
    volumes:
      - ../config:/app/config:ro  # Mount config folder (read-only)
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### test/Dockerfile.test

```dockerfile
# Runtime stage - Use pre-built binary (due to Go version issue)
FROM alpine:3.19

# Install dependencies
RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    curl

# Create app user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Set working directory
WORKDIR /app

# Copy pre-built binary from host
COPY bin/noti-service-linux /app/noti-service

# Copy config folder (FCM key will be mounted via volume)
COPY config /app/config

# Set permissions
RUN chmod +x /app/noti-service && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 9012

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the binary
ENTRYPOINT ["/app/noti-service"]
```

### 4. Build Prerequisites

#### Install Required Tools

**Windows (PowerShell):**
```powershell
# Chocolatey
choco install golang grpcurl protoc docker-desktop

# Or manually:
# Go: https://go.dev/dl/
# grpcurl: https://github.com/fullstorydev/grpcurl/releases
# Docker: https://docs.docker.com/desktop/install/windows-install/
```

**macOS:**
```bash
brew install go grpcurl protobuf docker
```

**Linux:**
```bash
# Go
wget https://go.dev/dl/go1.25.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.25.5.linux-amd64.tar.gz

# grpcurl
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### Verify Installation

```bash
go version          # Should show go1.25.x or higher
grpcurl --version   # Should show grpcurl version
docker --version    # Should show Docker version
```

---

## Implementation Details

### Files Modified/Created

| File | Change |
|------|--------|
| `internal/api/v1/notification.proto` | Added 3 RPC methods + request message |
| `internal/service/notification_grpc_service.go` | Added fcmAdapter, implemented handlers |
| `internal/server.go` | Pass fcmAdapter to service constructor |
| `internal/domain/models/event_registry.go` | **NEW** - Action code constants |
| `pkgs/pb/v1/*.go` | Regenerated from proto |

### Service Constructor Change

```go
// Before
func NewNotificationGRPCService(notiApp *notification.Application) *NotificationGRPCService

// After
func NewNotificationGRPCService(notiApp *notification.Application, fcmAdapter notifier.PushNotification) *NotificationGRPCService
```

### SendEventToDevices Logic

```go
func (s *NotificationGRPCService) SendEventToDevices(ctx context.Context, req *notificationv1.SendEventToDevicesRequest) (*notificationv1.BaseResponse, error) {
    // Build data payload
    data := make(map[string]string)
    data["action_code"] = req.ActionCode
    data["model"] = req.Model
    data["action"] = req.Action
    data["description"] = req.Description

    // Merge additional data
    for k, v := range req.Data {
        data[k] = v
    }

    // Send via FCM (### Docker
e

### Option 1: Run Locally

```bash
# Start noti-service
cd noti-service
go run cmd/main.go

# In another terminal, test with grpcurl
grpcurl -plaintext localhost:9012 list api.v1.NotificationService
```

### Option 2: Docker

```bash
# Build and run with docker-compose
cd noti-service
docker-compose -f test/docker-compose.test.yml up -d

# Check logs
docker logs noti_test_service -f

# Test
grpcurl -plaintext localhost:9012 list
```

### grpcurl Examples

**List methods:**
```bash
grpcurl -plaintext localhost:9012 list api.v1.NotificationService
```

**SendEventToDevices - Force Logout:**
```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["eAVmjf6OTJ6moEnc9W0s0_:APA91bE0_jshUq70Qt-TExQ3GgBhA8KFJi4PHQoIpCsujw9FaLZNaOlVO7iqI90qgtMXXCh5K0WZ8zFQHc7CR96YjhFxpNKGp2wjYDDRZSMasQKAz-yb7dA"],
  "actionCode": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Your supplier account has been deactivated"
}' localhost:9012 api.v1.NotificationService/SendEventToDevices
```

**SendNotificationToDevices:**
```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["eAVmjf6OTJ6moEnc9W0s0_:APA91bE0_jshUq70Qt-TExQ3GgBhA8KFJi4PHQoIpCsujw9FaLZNaOlVO7iqI90qgtMXXCh5K0WZ8zFQHc7CR96YjhFxpNKGp2wjYDDRZSMasQKAz-yb7dA"],
  "title": "Hello",
  "body": "Test notification",
  "data": {"key": "value"}
}' localhost:9012 api.v1.NotificationService/SendNotificationToDevices
```

**SendNotificationToTopic:**
```bash
grpcurl -plaintext -d '{
  "topic": "all_suppliers",
  "title": "System Update",
  "body": "New features available"
}' localhost:9012 api.v1.NotificationService/SendNotificationToTopic
```

### Get FCM Token from Mobile App

```bash
# Android
adb logcat | grep -i "fcm\|token"

# Or check app's debug screen
```

---

## Docker Setup

### Files Created

```
test/
├── Dockerfile.test           # Separate Dockerfile for testing
├── docker-compose.test.yml   # Compose with postgres + redis
├── config.test.yaml          # Test configuration (optional)
└── test_grpcurl.sh           # Testing script (optional)
```

### Complete Setup Steps

#### Step 1: Verify FCM Key Exists

```bash
# Check FCM key file
ls -l config/fcm-dev-sdk.json

# If not exists, download from Firebase Console (see Configuration Setup section)
```

#### Step 2: Build Linux Binary

**Why:** Docker image uses older Go version, need pre-built binary.

```bash
# Windows PowerShell
cd noti-service
$env:CGO_ENABLED="0"
$env:GOOS="linux"
$env:GOARCH="amd64"
go build -o bin/noti-service-linux ./cmd/main.go

# Linux/macOS
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o bin/noti-service-linux ./cmd/main.go

# Verify binary created
ls -lh bin/noti-service-linux
```

#### Step 3: Build Docker Image

```bash
# Build all services
cd test
docker-compose -f docker-compose.test.yml build

# Force rebuild without cache
docker-compose -f docker-compose.test.yml build --no-cache
```

#### Step 4: Start Services

```bash
# Start in background
docker-compose -f docker-compose.test.yml up -d

# Or start with logs visible
docker-compose -f docker-compose.test.yml up

# Wait for services to be healthy (10-15 seconds)
sleep 15
```

#### Step 5: Verify Services Running

```bash
# Check container status
docker-compose -f docker-compose.test.yml ps

# Expected output:
# NAME                    STATUS          PORTS
# noti-service-app        Up (healthy)    0.0.0.0:8000->8000/tcp, 0.0.0.0:9012->9012/tcp
# noti-service-postgres   Up (healthy)    0.0.0.0:5433->5432/tcp
# noti-service-redis      Up (healthy)    0.0.0.0:6380->6379/tcp
```

#### Step 6: View Logs

```bash
# All services
docker-compose -f docker-compose.test.yml logs -f

# Only noti-service
docker-compose -f docker-compose.test.yml logs -f noti-service

# Last 50 lines
docker logs noti-service-app --tail 50 -f
```

#### Step 7: Test gRPC Connection

```bash
# List available services
grpcurl -plaintext localhost:9012 list

# Should show:
# api.v1.NotificationService
# grpc.reflection.v1alpha.ServerReflection

# List methods
grpcurl -plaintext localhost:9012 list api.v1.NotificationService
```

### Stop and Cleanup

```bash
# Stop services (keep data)
docker-compose -f test/docker-compose.test.yml stop

# Stop and remove containers
docker-compose -f test/docker-compose.test.yml down

# Remove containers + volumes (delete data)
docker-compose -f test/docker-compose.test.yml down -v

# Full cleanup (remove images too)
docker-compose -f test/docker-compose.test.yml down -v --rmi all
```

### Restart Single Service

```bash
# Restart noti-service only
docker-compose -f test/docker-compose.test.yml restart noti-service

# Rebuild and restart
docker-compose -f test/docker-compose.test.yml up -d --build noti-service
```

### Ports Used (Test)

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5433 | Avoid conflict with local (5432) |
| Redis | 6380 | Avoid conflict with local (6379) |
| Noti HTTP | 8000 | Fiber HTTP |
| Noti gRPC | 9012 | gRPC |

---

## Mobile App Integration

### FCM Message Handler

```javascript
// React Native example
import messaging from '@react-native-firebase/messaging';

messaging().onMessage(async (remoteMessage) => {
  const data = remoteMessage.data;
  
  switch (data.action_code) {
    case '001': // Supplier deactivate
    case '002': // Buyer deactivate
      await clearAuthToken();
      navigation.reset({ routes: [{ name: 'Login' }] });
      break;
      
    case '101': // Supplier approved
      showToast('Your registration has been approved!');
      break;
      
    default:
      console.log('Unknown action:', data.action_code);
  }
});
```

### Background Handler

```javascript
// index.js - Must be at top level
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  const data = remoteMessage.data;
  
  if (['001', '002', '003', '004'].includes(data.action_code)) {
    await AsyncStorage.setItem('FORCE_LOGOUT', 'true');
  }
});
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Port 9012 in use | ASUS Armoury Crate (Windows) | Use port 9012 |
| FCM token invalid | Token expired or from emulator | Get fresh token from physical device |
| gRPC connection refused | Service not running | Check `docker logs` or `go run` output |
| Proto changes not reflected | Forgot to regenerate | Run `buf generate` |

### Check Service Status

```bash
# Local
lsof -i :9012  # Linux/Mac
netstat -ano | findstr :9012  # Windows

# Docker
docker ps
docker logs noti_test_service --tail 50
```

### Validate FCM Credentials

```bash
# Check if file exists
ls -la fcm-*.json

# Verify JSON format
cat fcm-dev-sdk.json | jq .
```

---

## Future Enhancements

1. **CAS Integration**: CAS calls noti-service when deactivating accounts
2. **SendEventToUser**: Look up device tokens by account_id
3. **SendEventToTopic**: Broadcast events to topic subscribers
4. **Event Logging**: Store sent events in database for audit
5. **Rate Limiting**: Prevent spam per account_id

---

## Related Files

| File | Description |
|------|-------------|
| `docs/TOB37_IMPLEMENTATION.md` | This document |
| `docs/UPGRADE_PLAN.md` | Future upgrade plans |
| `docs/EXPERIENCE.md` | Development learnings |
| `test/` | Docker and testing files |
| `TOB-37/` | Demo mobile app and test scripts |

---

## Quick Reference

### Start Service
```bash
go run cmd/main.go
```

### Test gRPC
```bash
grpcurl -plaintext localhost:9012 list
```

### Docker Test
```bash
docker-compose -f test/docker-compose.test.yml up -d
```

### Regenerate Proto
```bash
buf generate
```
