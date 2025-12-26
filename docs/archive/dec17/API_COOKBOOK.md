# 🍳 API COOKBOOK - Quick Reference Guide
**Copy-Paste Ready Commands for gRPC & REST API Testing**

**Last Updated:** December 17, 2025  
**Services:** Centre-Auth-Service + API Gateway

---

## 📋 TABLE OF CONTENTS

1. [REST API Commands](#rest-api-commands)
2. [gRPC Commands](#grpc-commands)
3. [Common Variables](#common-variables)
4. [Response Codes](#response-codes)

---

## 🌐 REST API COMMANDS

### Base URLs
```bash
# Development
GATEWAY_URL="http://localhost:8080"
AUTH_SERVICE_URL="http://localhost:4000"

# Production (example)
GATEWAY_URL="https://dev-api.agrios.vn/app"
```

---

### 🔹 Health Check

#### Check Gateway Health
```bash
curl http://localhost:8080/gateway/health
```

#### Check Services Status
```bash
curl http://localhost:8080/gateway/services
```

---

### 🔹 1. CHECK PHONE

Check if phone number is already registered.

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/check-phone' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369"
}'
```

#### With Variables
```bash
PHONE="0338636369"
curl -s http://localhost:8080/api/v1/cas/auth/check-phone \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\"}"
```

#### Expected Response (Available)
```json
{
  "code": "000",
  "message": "success",
  "data": {
    "exists": false,
    "phone_number": "0338636369"
  }
}
```

#### Expected Response (Already Exists)
```json
{
  "code": "000",
  "message": "success",
  "data": {
    "exists": true,
    "phone_number": "0338636369"
  }
}
```

---

### 🔹 2. SEND REGISTRATION OTP

Send OTP code for registration.

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/otp-register' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369"
}'
```

#### With Error Handling
```bash
PHONE="0338636369"
RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/otp-register \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\"}")

echo "$RESPONSE" | jq .

# Check success
if [[ $(echo "$RESPONSE" | jq -r '.code') == "000" ]]; then
  echo "✓ OTP sent successfully"
else
  echo "✗ Failed to send OTP"
fi
```

#### Expected Response
```json
{
  "code": "000",
  "message": "success",
  "data": {
    "phone_number": "0338636369",
    "purpose": "register",
    "expires_at": "2025-12-17T10:15:00Z"
  }
}
```

---

### 🔹 3. VERIFY OTP

Verify OTP code for registration or reset PIN.

#### For Registration
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/check-otp' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369",
  "otp_code": "123456",
  "purpose": "register"
}'
```

#### For Reset PIN
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/check-otp' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369",
  "otp_code": "654321",
  "purpose": "reset_pin"
}'
```

#### Save OTP ID for Next Step
```bash
PHONE="0338636369"
OTP_CODE="123456"

RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/check-otp \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\", \"otp_code\": \"$OTP_CODE\", \"purpose\": \"register\"}")

OTP_ID=$(echo "$RESPONSE" | jq -r '.data.otp_id')
echo "OTP ID: $OTP_ID"
```

#### Expected Response
```json
{
  "code": "000",
  "message": "success",
  "data": {
    "is_valid": true,
    "otp_id": "8efbccc9-9b8f-4ebf-a751-d2a6d4743e73",
    "message": "OTP hợp lệ."
  }
}
```

---

### 🔹 4. REGISTER

Complete registration with verified OTP.

#### Minimal
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/register' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369",
  "pin": "111111",
  "otp_id": "6574c5ab-121f-4b07-a97a-bf8d37f1d1d7",
  "name": "Test User 01",
  "device_info": {
    "device_id": "test_device_001",
    "device_type": "android"
  }
}'
```

#### Full with All Fields
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/register' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369",
  "pin": "111111",
  "otp_id": "8efbccc9-9b8f-4ebf-a751-d2a6d4743e73",
  "name": "Nguyễn Văn A",
  "date_of_birth": "1990-01-15",
  "gender": "male",
  "device_info": {
    "firebase_token": "fcm_token_abc123",
    "device_id": "device_unique_id_12345",
    "device_type": "android",
    "device_name": "Samsung Galaxy S23",
    "os_version": "Android 13",
    "app_version": "1.0.0",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0 (Android)"
  }
}'
```

#### With Variable Substitution
```bash
PHONE="0338636369"
PIN="111111"
OTP_ID="6574c5ab-121f-4b07-a97a-bf8d37f1d1d7"
NAME="Test User 01"

RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/register \
  -H 'Content-Type: application/json' \
  -d "{
    \"phone_number\": \"$PHONE\",
    \"pin\": \"$PIN\",
    \"otp_id\": \"$OTP_ID\",
    \"name\": \"$NAME\",
    \"device_info\": {
      \"device_id\": \"test_device\",
      \"device_type\": \"android\"
    }
  }")

ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.data.access_token')
ACCOUNT_CODE=$(echo "$RESPONSE" | jq -r '.data.account.code')

echo "Access Token: $ACCESS_TOKEN"
echo "Account Code: $ACCOUNT_CODE"
```

#### Expected Response
```json
{
  "code": "000",
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "2691334ede7eeb7caf97691e651059f5...",
    "account": {
      "id": "1",
      "code": "fuTiNuoI",
      "identifier": "0338636369",
      "name": "Test User",
      "is_farmer": false,
      "is_supplier": false,
      "is_ekyc": false
    }
  }
}
```

---

### 🔹 5. LOGIN

Login with phone number and PIN.

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/login' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369",
  "pin": "111111",
  "device_info": {
    "device_id": "test_device_001",
    "device_type": "android"
  }
}'
```

#### Full with All Device Info
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/login' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369",
  "pin": "111111",
  "device_info": {
    "firebase_token": "fcm_token_login",
    "device_id": "device_login_12345",
    "device_type": "android",
    "device_name": "Samsung Galaxy A30",
    "os_version": "Android 13",
    "app_version": "1.0.0"
  }
}'
```

#### Save Access Token
```bash
PHONE="0338636369"
PIN="111111"

RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/login \
  -H 'Content-Type: application/json' \
  -d "{
    \"phone_number\": \"$PHONE\",
    \"pin\": \"$PIN\",
    \"device_info\": {
      \"device_id\": \"test_device\",
      \"device_type\": \"android\"
    }
  }")

ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.data.access_token')
REFRESH_TOKEN=$(echo "$RESPONSE" | jq -r '.data.refresh_token')

echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"

# Export for other commands
export ACCESS_TOKEN
```

#### Expected Response
```json
{
  "code": "000",
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "59e38f016a99f0cf47c98334618c601e...",
    "account": {
      "id": "1",
      "code": "fuTiNuoI",
      "identifier": "0338636369",
      "name": "Test User"
    }
  }
}
```

---

### 🔹 6. SEND RESET PIN OTP

Send OTP for resetting PIN (forgot PIN flow).

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/otp-reset-pin' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369"
}'
```

#### With Variables
```bash
PHONE="0338636369"

curl -s http://localhost:8080/api/v1/cas/auth/otp-reset-pin \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\"}"
```

#### Expected Response
```json
{
  "code": "000",
  "message": "success",
  "data": {
    "phone_number": "0338636369",
    "purpose": "reset_pin",
    "expires_at": "2025-12-17T10:20:00Z"
  }
}
```

---

### 🔹 7. RESET PIN

Reset PIN using verified OTP.

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/reset-pin' \
--header 'Content-Type: application/json' \
--data '{
  "phone_number": "0338636369",
  "otp_id": "185927dc-aa57-4d94-88ce-2c3c36d0c0b9",
  "new_pin": "222222"
}'
```

#### With Variables
```bash
PHONE="0338636369"
OTP_ID="185927dc-aa57-4d94-88ce-2c3c36d0c0b9"
NEW_PIN="222222"

curl -s http://localhost:8080/api/v1/cas/auth/reset-pin \
  -H 'Content-Type: application/json' \
  -d "{
    \"phone_number\": \"$PHONE\",
    \"otp_id\": \"$OTP_ID\",
    \"new_pin\": \"$NEW_PIN\"
  }"
```

#### Expected Response
```json
{
  "code": "000",
  "message": "success",
  "data": null
}
```

**Note:** All old tokens are revoked. User must login again.

---

### 🔹 8. CHANGE PIN

Change PIN when user knows old PIN (authenticated).

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/auth/change-pin' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--data '{
  "old_pin": "111111",
  "new_pin": "222222"
}'
```

#### With Variables
```bash
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
OLD_PIN="111111"
NEW_PIN="222222"

curl -s http://localhost:8080/api/v1/cas/auth/change-pin \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"old_pin\": \"$OLD_PIN\",
    \"new_pin\": \"$NEW_PIN\"
  }"
```

#### Expected Response
```json
{
  "code": "000",
  "message": "success",
  "data": null
}
```

**Note:** All old tokens are revoked. User must login again.

---

### 🔹 9. eKYC VERIFICATION

Verify identity with CCCD (Citizen ID).

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/ekyc/id/verify' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--data '{
  "cccd": "044195000123",
  "dg1": "base64_encoded_data_1",
  "dg13": "base64_encoded_data_13",
  "dg2": "base64_encoded_data_2",
  "sod": "base64_encoded_sod"
}'
```

#### With Mock Data (Development)
```bash
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -s http://localhost:8080/api/v1/cas/ekyc/id/verify \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "cccd": "044195000123",
    "dg1": "111111",
    "dg13": "111111",
    "dg2": "111111",
    "sod": "111111"
  }'
```

---

### 🔹 10. CHECK CONSENT

Check if user has given consent.

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/consents?consent_type=share_frm_data' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

#### With Variables
```bash
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
CONSENT_TYPE="share_frm_data"

curl -s "http://localhost:8080/api/v1/cas/consents?consent_type=$CONSENT_TYPE" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### 🔹 11. CREATE CONSENT

Create user consent.

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/consents' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--data '{
  "consent_type": "share_frm_data",
  "policy_type_id": 1
}'
```

---

### 🔹 12. CHECK FRM FARMER

Check if user exists in FRM system.

#### Basic
```bash
curl --location 'http://localhost:8080/api/v1/cas/frm-farmers/check' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--data ''
```

---

### 🔹 13. CREATE FARMER PROFILE

Create farmer profile (onboarding).

#### Full Example
```bash
curl --location 'http://localhost:8080/api/v1/cas/farmers' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
--data '{
  "agricultural_officer": "Nguyễn Văn A",
  "area": 15.5,
  "avatar_url": "https://example.com/images/avatar/24761.jpg",
  "crop_types": ["Mía", "Lúa", "Bắp"],
  "cultivated_area": {
    "address": "83 Nguyễn Văn Đậu",
    "district": {
      "id": "1",
      "value": "Gò Vấp"
    },
    "province": {
      "id": "2",
      "value": "Ho Chi Minh"
    },
    "ward_commune": {
      "id": "2",
      "value": "Phường 3"
    }
  },
  "customer_code": "24761",
  "customer_group": "Nhóm khách hàng Bạc",
  "customer_type": "Nông dân",
  "img_back_url": "https://example.com/images/idcard/24761_back.jpg",
  "img_front_url": "https://example.com/images/idcard/24761_front.jpg",
  "investment_area": "Miền Đông",
  "investment_programs": ["Hỗ trợ giống", "Vay vốn lãi suất ưu đãi"],
  "investment_zone": "Khu vực Tây Ninh",
  "status": "Chính thức",
  "is_skip": false
}'
```

---

## 🔧 gRPC COMMANDS

### Setup grpcurl

#### Install (if not already)
```bash
# macOS
brew install grpcurl

# Linux
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Windows
# Download from: https://github.com/fullstorydev/grpcurl/releases
```

#### List Available Services
```bash
grpcurl -plaintext localhost:50051 list
```

#### Describe Service
```bash
grpcurl -plaintext localhost:50051 describe cas.AuthService
```

---

### 🔹 gRPC: Check Phone

```bash
grpcurl -plaintext \
  -d '{
    "phone_number": "0338636369"
  }' \
  localhost:50051 \
  cas.AuthService/CheckPhone
```

---

### 🔹 gRPC: Send Register OTP

```bash
grpcurl -plaintext \
  -d '{
    "phone_number": "0338636369"
  }' \
  localhost:50051 \
  cas.AuthService/SendRegisterOTP
```

---

### 🔹 gRPC: Verify OTP

```bash
grpcurl -plaintext \
  -d '{
    "phone_number": "0338636369",
    "otp_code": "123456",
    "purpose": "register"
  }' \
  localhost:50051 \
  cas.AuthService/VerifyOTP
```

---

### 🔹 gRPC: Register

```bash
grpcurl -plaintext \
  -d '{
    "phone_number": "0338636369",
    "pin": "111111",
    "otp_id": "8efbccc9-9b8f-4ebf-a751-d2a6d4743e73",
    "name": "Test User",
    "device_info": {
      "device_id": "test_device_001",
      "device_type": "android"
    }
  }' \
  localhost:50051 \
  cas.AuthService/Register
```

---

### 🔹 gRPC: Login

```bash
grpcurl -plaintext \
  -d '{
    "phone_number": "0338636369",
    "pin": "111111",
    "device_info": {
      "device_id": "test_device_login",
      "device_type": "android"
    }
  }' \
  localhost:50051 \
  cas.AuthService/Login
```

---

### 🔹 gRPC: Reset PIN

```bash
# Step 1: Send OTP
grpcurl -plaintext \
  -d '{"phone_number": "0338636369"}' \
  localhost:50051 \
  cas.AuthService/SendResetPINOTP

# Step 2: Verify OTP
grpcurl -plaintext \
  -d '{
    "phone_number": "0338636369",
    "otp_code": "654321",
    "purpose": "reset_pin"
  }' \
  localhost:50051 \
  cas.AuthService/VerifyOTP

# Step 3: Reset PIN
grpcurl -plaintext \
  -d '{
    "phone_number": "0338636369",
    "otp_id": "UUID_FROM_STEP_2",
    "new_pin": "222222"
  }' \
  localhost:50051 \
  cas.AuthService/ResetPIN
```

---

### 🔹 gRPC: Change PIN (with Auth)

```bash
# Get metadata with token
grpcurl -plaintext \
  -H "authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "old_pin": "111111",
    "new_pin": "222222"
  }' \
  localhost:50051 \
  cas.AuthService/ChangePIN
```

---

## 📦 COMMON VARIABLES

### Environment Variables
```bash
# URLs
export GATEWAY_URL="http://localhost:8080"
export AUTH_SERVICE_URL="http://localhost:4000"
export GRPC_URL="localhost:50051"

# Test Data
export TEST_PHONE="09$(date +%s | tail -c 9)"
export TEST_PIN="111111"
export TEST_NAME="Test User $(date +%H%M%S)"

# Credentials (after login)
export ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export REFRESH_TOKEN="2691334ede7eeb7caf97691e651059f5..."
export ACCOUNT_CODE="fuTiNuoI"
```

### Device Info Template
```bash
DEVICE_INFO='{
  "firebase_token": "fcm_token_abc123",
  "device_id": "device_unique_id_12345",
  "device_type": "android",
  "device_name": "Samsung Galaxy S23",
  "os_version": "Android 13",
  "app_version": "1.0.0",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Android)"
}'
```

---

## 🎨 CURL OPTIONS

### Useful Flags
```bash
# Silent mode (no progress)
curl -s URL

# Include response headers
curl -i URL

# Verbose output (debug)
curl -v URL

# Follow redirects
curl -L URL

# Save output to file
curl -o output.json URL

# Show only HTTP status code
curl -s -o /dev/null -w "%{http_code}" URL

# Timeout
curl --max-time 10 URL

# Retry on failure
curl --retry 3 URL
```

### Pretty Print JSON
```bash
# Using jq
curl -s URL | jq .

# Specific field
curl -s URL | jq '.data.access_token'

# Colored output
curl -s URL | jq -C . | less -R
```

---

## 📊 RESPONSE CODES

### Success Codes
| Code | Message | Description |
|------|---------|-------------|
| 000 | success | Operation successful |
| 200 | OK | HTTP success |
| 201 | Created | Resource created |

### Error Codes
| Code | Message | Description |
|------|---------|-------------|
| 001 | validation error | Invalid input |
| 002 | phone already registered | Phone exists |
| 003 | invalid OTP | OTP incorrect |
| 004 | request timeout | Service timeout |
| 013 | SMS service unavailable | Notification service down |
| 401 | unauthorized | Invalid/missing token |
| 404 | not found | Resource not found |
| 500 | internal server error | Server error |

---

## 🔄 COMPLETE FLOW EXAMPLES

### Flow 1: Registration
```bash
# Variables
PHONE="09$(date +%s | tail -c 9)"
PIN="111111"

# Step 1: Check phone
curl -s http://localhost:8080/api/v1/cas/auth/check-phone \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\"}"

# Step 2: Send OTP
curl -s http://localhost:8080/api/v1/cas/auth/otp-register \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\"}"

# Step 3: Verify OTP (enter OTP from Telegram)
read -p "Enter OTP: " OTP_CODE
RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/check-otp \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\", \"otp_code\": \"$OTP_CODE\", \"purpose\": \"register\"}")
OTP_ID=$(echo "$RESPONSE" | jq -r '.data.otp_id')

# Step 4: Register
RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/register \
  -H 'Content-Type: application/json' \
  -d "{
    \"phone_number\": \"$PHONE\",
    \"pin\": \"$PIN\",
    \"otp_id\": \"$OTP_ID\",
    \"name\": \"Test User\",
    \"device_info\": {\"device_id\": \"test\", \"device_type\": \"android\"}
  }")

ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.data.access_token')
echo "Access Token: $ACCESS_TOKEN"
```

### Flow 2: Login
```bash
PHONE="0338636369"
PIN="111111"

RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/login \
  -H 'Content-Type: application/json' \
  -d "{
    \"phone_number\": \"$PHONE\",
    \"pin\": \"$PIN\",
    \"device_info\": {\"device_id\": \"test\", \"device_type\": \"android\"}
  }")

ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.data.access_token')
export ACCESS_TOKEN
```

### Flow 3: Reset PIN
```bash
PHONE="0338636369"
NEW_PIN="222222"

# Step 1: Send reset OTP
curl -s http://localhost:8080/api/v1/cas/auth/otp-reset-pin \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\"}"

# Step 2: Verify OTP
read -p "Enter reset OTP: " RESET_OTP
RESPONSE=$(curl -s http://localhost:8080/api/v1/cas/auth/check-otp \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\", \"otp_code\": \"$RESET_OTP\", \"purpose\": \"reset_pin\"}")
OTP_ID=$(echo "$RESPONSE" | jq -r '.data.otp_id')

# Step 3: Reset PIN
curl -s http://localhost:8080/api/v1/cas/auth/reset-pin \
  -H 'Content-Type: application/json' \
  -d "{\"phone_number\": \"$PHONE\", \"otp_id\": \"$OTP_ID\", \"new_pin\": \"$NEW_PIN\"}"
```

---

## 🛠️ TROUBLESHOOTING

### Debug Request/Response
```bash
# Show full request and response
curl -v http://localhost:8080/api/v1/cas/auth/check-phone \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "0338636369"}'

# Save response for analysis
curl -s http://localhost:8080/api/v1/cas/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "0338636369", "pin": "111111", "device_info": {...}}' \
  > response.json

cat response.json | jq .
```

### Check Service Status
```bash
# Gateway health
curl http://localhost:8080/gateway/health

# Services list
curl http://localhost:8080/gateway/services | jq .

# gRPC service availability
grpcurl -plaintext localhost:50051 list
```

### Common Issues

#### "Connection refused"
```bash
# Check if services are running
ps aux | grep "bin/app"

# Check ports
netstat -ano | grep :8080
netstat -ano | grep :50051
```

#### "Invalid token"
```bash
# Token might be expired - get new one
curl -s http://localhost:8080/api/v1/cas/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"phone_number": "YOUR_PHONE", "pin": "YOUR_PIN", "device_info": {...}}' \
  | jq -r '.data.access_token'
```

#### "OTP invalid"
```bash
# Check OTP in service logs
tail -f centre-auth-service/logs/app.log | grep otp_code

# Or check Telegram messages
```

---

## 📝 NOTES

### Token Management
- Access token expires in 15 minutes
- Refresh token expires in 7 days
- Save tokens after login for subsequent requests
- Use `export ACCESS_TOKEN="..."` to reuse in terminal

### Phone Numbers
- Format: 10 digits starting with 0 (e.g., 0338636369)
- Generate unique: `09$(date +%s | tail -c 9)`

### PINs
- Must be exactly 6 digits
- Stored as bcrypt hash in database
- Never logged or transmitted in plain text (except during login/register)

### OTP
- Valid for 2 minutes (120 seconds)
- Can be used only once
- Rate limit: 5 OTP per day per phone
- Cooldown: 60 seconds between requests

---

**Last Updated:** December 17, 2025  
**Maintained By:** @thatlq1812

**Quick Tip:** Use `Ctrl+F` to search for specific endpoints or commands!
