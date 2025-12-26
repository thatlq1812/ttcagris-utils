# Hướng Dẫn Chạy Noti Service với Docker

**Tác giả:** GitHub Copilot  
**Ngày tạo:** 2025-12-24  
**Cập nhật:** 2025-12-24

## Mục Lục
1. [Giới Thiệu](#giới-thiệu)
2. [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
3. [Clone Repository](#clone-repository)
4. [Cấu Hình Service](#cấu-hình-service)
5. [Build Binary Trước](#build-binary-trước)
6. [Chạy Docker Compose](#chạy-docker-compose)
7. [Kiểm Tra Service](#kiểm-tra-service)
8. [Các Lệnh grpcurl Test](#các-lệnh-grpcurl-test)
9. [Troubleshooting](#troubleshooting)

---

## Giới Thiệu

Tài liệu này hướng dẫn cách clone và chạy **noti-service** (Notification Service) bằng Docker để test chức năng gửi thông báo FCM đến mobile app.

**Tính năng chính:**
- Gửi notification đến các device thông qua FCM token
- Hỗ trợ force logout (action code 001)
- gRPC API trên port 9012
- HTTP/REST API trên port 8000

---

## Yêu Cầu Hệ Thống

### Phần Mềm Cần Cài Đặt

- **Docker Desktop**: Phiên bản mới nhất
- **Go**: Version 1.25.x hoặc cao hơn (để build binary)
- **grpcurl**: Công cụ test gRPC API
  ```bash
  # Windows (Chocolatey)
  choco install grpcurl
  
  # macOS
  brew install grpcurl
  
  # Linux
  go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
  ```

### Kiểm Tra Cài Đặt

```bash
# Kiểm tra Docker
docker --version
docker-compose --version

# Kiểm tra Go
go version

# Kiểm tra grpcurl
grpcurl --version
```

---

## Clone Repository

### 1. Clone Repo Từ Azure DevOps

```bash
# Di chuyển đến thư mục làm việc
cd D:\projects

# Clone repository (thay YOUR_PAT bằng Personal Access Token của bạn)
git clone https://YOUR_PAT@dev.azure.com/agris-agriculture/AgriOS/_git/noti-service
cd noti-service

# Hoặc nếu đã có repo, pull code mới nhất
git pull origin main
```

### 2. Kiểm Tra Cấu Trúc Thư Mục

Sau khi clone, bạn sẽ có cấu trúc như sau:

```
noti-service/
├── cmd/
│   └── main.go
├── config/
│   └── config.yaml
├── test/
│   ├── docker-compose.test.yml
│   └── Dockerfile.test
├── go.mod
├── Makefile
└── README.md
```

---

## Cấu Hình Service

### 1. File Cấu Hình FCM

Đảm bảo file FCM service account key đã tồn tại:

```bash
# File này chứa credentials để kết nối Firebase
ls config/fcm-dev-sdk.json
```

> **Lưu ý:** File này chứa thông tin nhạy cảm, không được commit lên Git.

### 2. Kiểm Tra Config YAML

Mở file [config/config.yaml](noti-service/config/config.yaml) và kiểm tra các thông số:

```yaml
server:
  env: development
  grpc_port: 9012      # Port gRPC
  http_port: 8000      # Port HTTP/REST

firebase:
  credentials_path: config/fcm-dev-sdk.json
  project_id: agrios-notification-demo

database:
  host: postgres
  port: 5432
  # ...các config khác
```

---

## Build Binary Trước

Do vấn đề về Go version trong Docker image, chúng ta cần **build binary trước** rồi copy vào container.

### 1. Build Binary Linux

```bash
# Di chuyển đến thư mục noti-service
cd D:\ttcagris\noti-service

# Build binary cho Linux (Alpine)
$env:CGO_ENABLED="0"
$env:GOOS="linux"
$env:GOARCH="amd64"
go build -o bin/noti-service-linux ./cmd/main.go

# Kiểm tra binary đã tạo
ls bin/noti-service-linux
```

**Output mong đợi:**
```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          24/12/2025  10:30 AM       45678912 noti-service-linux
```

### 2. Giải Thích Các Flags

- `CGO_ENABLED=0`: Tắt CGO, tạo static binary
- `GOOS=linux`: Build cho Linux OS
- `GOARCH=amd64`: Build cho CPU 64-bit
- `-o bin/noti-service-linux`: Output file path

---

## Chạy Docker Compose

### 1. Di Chuyển Đến Thư Mục Test

```bash
cd test
```

### 2. Build và Start Containers

```bash
# Build image và start tất cả services
docker-compose -f docker-compose.test.yml up -d

# Hoặc force rebuild nếu có thay đổi
docker-compose -f docker-compose.test.yml up -d --build
```

### 3. Kiểm Tra Containers Đang Chạy

```bash
docker-compose -f docker-compose.test.yml ps
```

**Output mong đợi:**
```
NAME                    IMAGE                   STATUS       PORTS
noti-service-app        noti-service-test       Up 30s       0.0.0.0:8000->8000/tcp, 0.0.0.0:9012->9012/tcp
noti-service-postgres   postgres:17-alpine      Up 30s       5432/tcp
noti-service-redis      redis:7-alpine          Up 30s       6379/tcp
```

### 4. Xem Logs

```bash
# Xem logs của noti-service
docker-compose -f docker-compose.test.yml logs -f noti-service

# Xem logs tất cả services
docker-compose -f docker-compose.test.yml logs -f
```

**Log thành công sẽ hiển thị:**
```
noti-service | INFO: gRPC server listening on :9012
noti-service | INFO: HTTP server listening on :8000
noti-service | INFO: Database connected successfully
noti-service | INFO: Redis connected successfully
```

---

## Kiểm Tra Service

### 1. Health Check

```bash
# Kiểm tra HTTP health endpoint
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-24T10:30:00Z"
}
```

### 2. List gRPC Services

```bash
# Liệt kê tất cả services
grpcurl -plaintext localhost:9012 list
```

**Output:**
```
api.v1.CourierService
api.v1.NotificationService
api.v1.WebhookService
grpc.reflection.v1alpha.ServerReflection
```

### 3. List Methods Của NotificationService

```bash
# Liệt kê các methods
grpcurl -plaintext localhost:9012 list api.v1.NotificationService
```

**Output:**
```
api.v1.NotificationService.SendEventToDevices
api.v1.NotificationService.SendNotificationToDevices
api.v1.NotificationService.SendNotificationToTopic
api.v1.NotificationService.SendNotificationToTokens
api.v1.NotificationService.SendSilentNotificationToDevices
api.v1.NotificationService.SendSystemEventToDevices
api.v1.NotificationService.GetDeviceToken
api.v1.NotificationService.RegisterDeviceToken
api.v1.NotificationService.UnregisterDeviceToken
```

---

## Các Lệnh grpcurl Test

### 1. Lấy FCM Token Từ Mobile App

**Trên điện thoại:**
1. Mở app đã cài đặt
2. Đăng nhập bằng nút **Quick Login (Demo)**
3. Nhấn nút **Copy Token** trên màn hình Home
4. FCM token đã được copy vào clipboard

**Ví dụ FCM token:**
```
cwv6o7R3THiaLdRcpeEp_D:APA91bFXHco-bF1IK8Ft8HxEn0ibGwUfz-LEA2uE5WBhF4MExzDD68n6dA16MpfHf0p0S4Re3M2PiyS-Or4NwjexTaT_SAnBQQ9neHH4y6cQo4z3zrhqX-k
```

### 2. Test Force Logout (Action 001)

```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN_HERE"],
  "actionCode": "001",
  "model": "suppliers",
  "action": "deactivate",
  "description": "Your supplier account has been deactivated"
}' localhost:9012 api.v1.NotificationService/SendEventToDevices
```

**Response thành công:**
```json
{
  "success": true,
  "successCount": "1",
  "failureCount": "0"
}
```

### 3. Test Notification Thường

```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN_HERE"],
  "notification": {
    "title": "Test Notification",
    "body": "This is a test message from noti-service",
    "imageUrl": ""
  },
  "data": {
    "type": "test",
    "timestamp": "2025-12-24T10:30:00Z"
  }
}' localhost:9012 api.v1.NotificationService/SendNotificationToDevices
```

### 4. Test Silent Notification

```bash
grpcurl -plaintext -d '{
  "deviceTokens": ["YOUR_FCM_TOKEN_HERE"],
  "data": {
    "action": "sync",
    "timestamp": "2025-12-24T10:30:00Z"
  }
}' localhost:9012 api.v1.NotificationService/SendSilentNotificationToDevices
```

### 5. Test Gửi Đến Topic

```bash
grpcurl -plaintext -d '{
  "topic": "all-users",
  "notification": {
    "title": "System Announcement",
    "body": "Server maintenance at 2 AM",
    "imageUrl": ""
  }
}' localhost:9012 api.v1.NotificationService/SendNotificationToTopic
```

### 6. Inspect Method Schema

Xem chi tiết request/response schema của method:

```bash
grpcurl -plaintext localhost:9012 describe api.v1.NotificationService.SendEventToDevices
```

---

## Troubleshooting

### Lỗi: Container Không Start

**Triệu chứng:**
```
Error: container exited with code 1
```

**Giải pháp:**
```bash
# Xem logs chi tiết
docker-compose -f test/docker-compose.test.yml logs noti-service

# Kiểm tra binary có tồn tại
ls bin/noti-service-linux

# Rebuild binary nếu cần
$env:CGO_ENABLED="0"
$env:GOOS="linux"
$env:GOARCH="amd64"
go build -o bin/noti-service-linux ./cmd/main.go
```

### Lỗi: Port Already In Use

**Triệu chứng:**
```
Error: bind: address already in use
```

**Giải pháp:**
```bash
# Kiểm tra process đang dùng port 9012
netstat -ano | findstr :9012

# Kill process (thay PID bằng số thực tế)
taskkill /PID <PID> /F

# Hoặc đổi port trong docker-compose.test.yml
ports:
  - "9013:9012"  # Đổi 9013 thành port khác
```

### Lỗi: grpcurl Connection Refused

**Triệu chứng:**
```
Error: Failed to dial target host "localhost:9012": dial tcp [::1]:9012: connect: connection refused
```

**Giải pháp:**
```bash
# 1. Kiểm tra container có đang chạy
docker-compose -f test/docker-compose.test.yml ps

# 2. Kiểm tra logs
docker-compose -f test/docker-compose.test.yml logs noti-service

# 3. Đợi service khởi động hoàn tất (10-15 giây)
timeout /t 15

# 4. Test lại
grpcurl -plaintext localhost:9012 list
```

### Lỗi: FCM Token Invalid

**Triệu chứng:**
```
{
  "success": false,
  "successCount": "0",
  "failureCount": "1"
}
```

**Giải pháp:**
1. Kiểm tra FCM token đã copy đúng (không có dấu cách thừa)
2. App phải đang chạy và có kết nối internet
3. FCM token có thể đã expire, mở lại app để lấy token mới
4. Kiểm tra file `fcm-dev-sdk.json` có đúng project không

### Lỗi: Database Connection Failed

**Triệu chứng:**
```
ERROR: failed to connect to database
```

**Giải pháp:**
```bash
# Kiểm tra postgres container
docker-compose -f test/docker-compose.test.yml ps postgres

# Restart postgres
docker-compose -f test/docker-compose.test.yml restart postgres

# Kiểm tra logs postgres
docker-compose -f test/docker-compose.test.yml logs postgres
```

---

## Dừng và Xóa Containers

### Dừng Services

```bash
# Dừng tất cả containers
docker-compose -f test/docker-compose.test.yml stop

# Hoặc dừng và xóa
docker-compose -f test/docker-compose.test.yml down
```

### Xóa Volumes (Dữ liệu database)

```bash
# Xóa containers và volumes
docker-compose -f test/docker-compose.test.yml down -v
```

### Clean Up Hoàn Toàn

```bash
# Xóa tất cả (containers, networks, volumes, images)
docker-compose -f test/docker-compose.test.yml down -v --rmi all
```

---

## Tham Khảo Thêm

### Tài Liệu Liên Quan

- [FCM_TESTING_GUIDE.md](FCM_TESTING_GUIDE.md) - Hướng dẫn test FCM chi tiết
- [noti-service/README.md](../../noti-service/README.md) - README chính của service
- [Core Proto Documentation](../../Core/README.md) - Proto definitions

### Useful Links

- **Firebase Console**: [https://console.firebase.google.com](https://console.firebase.google.com)
- **grpcurl GitHub**: [https://github.com/fullstorydev/grpcurl](https://github.com/fullstorydev/grpcurl)
- **Docker Compose Docs**: [https://docs.docker.com/compose](https://docs.docker.com/compose)

---

## Tóm Tắt Các Bước Chính

1. **Clone repository**:
   ```bash
   git clone https://YOUR_PAT@dev.azure.com/agris-agriculture/AgriOS/_git/noti-service
   cd noti-service
   ```

2. **Build binary**:
   ```bash
   $env:CGO_ENABLED="0"; $env:GOOS="linux"; $env:GOARCH="amd64"
   go build -o bin/noti-service-linux ./cmd/main.go
   ```

3. **Start Docker**:
   ```bash
   cd test
   docker-compose -f docker-compose.test.yml up -d
   ```

4. **Verify**:
   ```bash
   grpcurl -plaintext localhost:9012 list
   ```

5. **Test FCM**:
   ```bash
   grpcurl -plaintext -d '{"deviceTokens": ["YOUR_TOKEN"], "actionCode": "001", ...}' localhost:9012 api.v1.NotificationService/SendEventToDevices
   ```

---

**Chúc bạn test thành công!** 🎉
