# Centre Auth Service - Testing Guide

**Author:** thatlq1812  
**Created:** 2025-12-18  
**Last Updated:** 2025-12-18  
**Version:** 1.0.0  
**Status:** Active

---

## Overview

This guide provides comprehensive testing procedures for Centre Auth Service, including unit tests, integration tests, API testing, and manual testing scenarios.

**Testing Tools:**
- Unit Tests: Go testing framework with Testify
- API Tests: cURL, Postman, HTTPie
- gRPC Tests: grpcurl, BloomRPC
- Load Tests: k6, Apache Bench

---

## Prerequisites

### Required Setup

```bash
# 1. Start PostgreSQL
# Ensure PostgreSQL is running on localhost:5432

# 2. Start Redis
# Ensure Redis is running on localhost:6379

# 3. Create test database
createdb -U postgres centre_auth_test

# 4. Install testing tools
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
brew install httpie  # macOS
# or
apt install httpie   # Linux
```

### Environment Configuration

Create `config/config.test.yaml`:

```yaml
server:
  name: "centre-auth-service"
  port: "4001"           # Different port for testing
  env: "test"

grpc:
  enabled: true
  port: 50052            # Different gRPC port

database:
  host: "localhost"
  port: 5432
  username: "postgres"
  password: "postgres"
  database: "centre_auth_test"
  schema: "public"
  ssl_mode: "disable"

cache:
  redis:
    mode: "standalone"
    address:
      - "localhost:6379"
    db: 1                # Different Redis DB for tests

jwt:
  secret_key_web: "test-secret-web-key"
  secret_key_app: "test-secret-app-key"
  access_token_duration: 15m
  refresh_token_duration: 168h

otp:
  expire_seconds: 120
  max_per_day: 100       # Higher limit for testing
  cooldown_seconds: 5    # Shorter cooldown for testing
```

---

## Running Tests

### Unit Tests

```bash
# Run all tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run tests with detailed coverage
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Run specific package tests
go test ./internal/usecase/...

# Run with verbose output
go test -v ./internal/usecase/auth_usecase_test.go

# Run specific test function
go test -run TestAuthUsecase_Login ./internal/usecase/
```

### Integration Tests

```bash
# Start service in test mode
CONFIG_FILE=config/config.test.yaml make api

# Run integration tests (in another terminal)
go test -tags=integration ./tests/integration/...
```

### Benchmark Tests

```bash
# Run benchmark tests
go test -bench=. ./internal/usecase/...

# Run specific benchmark
go test -bench=BenchmarkLogin ./internal/usecase/
```

---

## API Testing via Gateway

### Setup

Start both services:

```bash
# Terminal 1: Start CAS
cd centre-auth-service
make api

# Terminal 2: Start Gateway
cd app-api-gateway
make api
```

Gateway runs on `http://localhost:8080`

---

## Authentication Flow Tests

### 1. Register New Account (Web)

**Test Case:** Register new user with email

```bash
# Using cURL
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "identifier": "john.doe@example.com",
    "password": "SecurePass123"
  }'

# Using HTTPie
http POST http://localhost:8080/api/v1/auth/register \
  name="John Doe" \
  identifier="john.doe@example.com" \
  password="SecurePass123"
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Registration successful",
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "account": {
      "id": 1,
      "type": "email",
      "identifier": "john.doe@example.com"
    }
  }
}
```

**Validation:**
- Status code: 200
- Response includes access_token and refresh_token
- Account type is "email"
- Account source is "web" (default)

---

### 2. Login

**Test Case:** Login with email and password

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "john.doe@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "account": {
      "id": 1,
      "identifier": "john.doe@example.com",
      "name": "John Doe",
      "is_ekyc": false,
      "is_farmer": false
    }
  }
}
```

**Validation:**
- Status code: 200
- New access_token and refresh_token issued
- Account details returned

---

### 3. Get Profile

**Test Case:** Get authenticated user profile

```bash
# Save access token from login
TOKEN="eyJhbGci..."

curl http://localhost:8080/api/v1/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Profile retrieved successfully",
  "data": {
    "account": {
      "id": 1,
      "identifier": "john.doe@example.com",
      "name": "John Doe",
      "email": "john.doe@example.com"
    }
  }
}
```

**Validation:**
- Status code: 200
- Account details match login response

---

### 4. Refresh Token

**Test Case:** Get new access token using refresh token

```bash
REFRESH_TOKEN="eyJhbGci..."

curl -X POST http://localhost:8080/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci..."
  }
}
```

**Validation:**
- Status code: 200
- New access_token and refresh_token issued
- Old refresh_token is invalidated

---

### 5. Logout

**Test Case:** Logout and invalidate tokens

```bash
curl -X POST http://localhost:8080/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Logout successful",
  "data": {
    "message": "User logged out successfully"
  }
}
```

**Validation:**
- Status code: 200
- Refresh token is revoked
- Subsequent API calls with old token fail with 401

---

## Mobile Authentication Flow Tests

### 1. Check Phone Exists

**Test Case:** Check if phone is registered

```bash
curl -X POST http://localhost:8080/api/v1/mobile/check-phone-exists \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+84901234567"
  }'
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Phone check completed",
  "data": {
    "exists": false
  }
}
```

---

### 2. Send Register OTP

**Test Case:** Request OTP for registration

```bash
curl -X POST http://localhost:8080/api/v1/mobile/send-register-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+84901234567"
  }'
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "OTP sent successfully",
  "data": {
    "code": "uuid-1234-5678",
    "message": "OTP sent successfully to Telegram",
    "expires_at": "2025-12-18T10:02:00+07:00"
  }
}
```

**Validation:**
- Status code: 200
- OTP code (UUID) returned
- Expiry time is 2 minutes from now
- Check Telegram bot for actual OTP code (in development mode)

---

### 3. Verify OTP

**Test Case:** Verify OTP before registration

```bash
OTP_ID="uuid-1234-5678"
OTP_CODE="123456"  # From Telegram

curl -X POST http://localhost:8080/api/v1/mobile/verify-otp \
  -H "Content-Type: application/json" \
  -d "{
    \"phone_number\": \"+84901234567\",
    \"otp_id\": \"$OTP_ID\",
    \"otp_code\": \"$OTP_CODE\"
  }"
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "OTP verified successfully",
  "data": {
    "verified": true,
    "grace_period_seconds": 180
  }
}
```

**Validation:**
- Status code: 200
- verified is true
- Grace period of 180 seconds to complete registration

---

### 4. Register Mobile Account

**Test Case:** Register after OTP verification

```bash
curl -X POST http://localhost:8080/api/v1/mobile/register \
  -H "Content-Type: application/json" \
  -d "{
    \"phone_number\": \"+84901234567\",
    \"otp_id\": \"$OTP_ID\",
    \"pin\": \"123456\",
    \"name\": \"John Mobile\",
    \"date_of_birth\": \"1990-01-15\",
    \"gender\": \"male\",
    \"device_info\": {
      \"device_id\": \"test-device-123\",
      \"device_type\": \"mobile\",
      \"device_name\": \"Test Phone\",
      \"os_version\": \"iOS 17.0\",
      \"app_version\": \"1.0.0\"
    }
  }"
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Registration successful",
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "account": {
      "id": 2,
      "identifier": "+84901234567",
      "code": "ABC12345",
      "name": "John Mobile"
    }
  }
}
```

**Validation:**
- Status code: 200
- Account code is 8 characters
- Account source is "app"
- Tokens issued

---

### 5. Login with PIN

**Test Case:** Login with phone and PIN

```bash
curl -X POST http://localhost:8080/api/v1/mobile/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+84901234567",
    "pin": "123456",
    "device_info": {
      "device_id": "test-device-123",
      "device_type": "mobile"
    }
  }'
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "account": {
      "id": 2,
      "identifier": "+84901234567",
      "code": "ABC12345",
      "name": "John Mobile"
    }
  }
}
```

---

### 6. Change PIN

**Test Case:** Change PIN (authenticated)

```bash
curl -X POST http://localhost:8080/api/v1/mobile/change-pin \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_pin": "123456",
    "new_pin": "654321"
  }'
```

**Expected Response:**
```json
{
  "code": "200",
  "message": "PIN changed successfully",
  "data": {
    "code": "200",
    "message": "PIN has been changed"
  }
}
```

---

## Account Management Tests

### 1. Get My Account

```bash
curl http://localhost:8080/api/v1/accounts/me \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Update My Account

```bash
curl -X PUT http://localhost:8080/api/v1/accounts/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "email": "john.updated@example.com",
    "address": "123 Main St"
  }'
```

### 3. List Accounts (Admin)

```bash
# With filters
curl "http://localhost:8080/api/v1/accounts?page=1&size=20&search=john" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Filter by source
curl "http://localhost:8080/api/v1/accounts?filters[0][field]=source&filters[0][operator]=\$eq&filters[0][values][0]=app" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Farmer Domain Tests

### 1. Create Farmer Profile

```bash
curl -X POST http://localhost:8080/api/v1/farmers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "area": 5000.5,
    "customer_code": "FARM001",
    "crop_types": ["rice", "corn"],
    "status": "active"
  }'
```

### 2. Get My Farmer Profile

```bash
curl http://localhost:8080/api/v1/farmers/me \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Update Farmer Profile

```bash
curl -X PUT http://localhost:8080/api/v1/farmers/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "area": 6000.0,
    "crop_types": ["rice", "corn", "vegetables"]
  }'
```

---

## Role & Permission Tests

### 1. List All Permissions

```bash
curl http://localhost:8080/api/v1/permissions
```

### 2. Create Role

```bash
curl -X POST http://localhost:8080/api/v1/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Farmer Manager",
    "description": "Manages farmer accounts",
    "permission_ids": [1, 2, 3, 5]
  }'
```

### 3. Assign Role to Account

```bash
curl -X POST http://localhost:8080/api/v1/roles/assign \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 123,
    "role_code": "farmer_manager",
    "domain": "HUB001"
  }'
```

### 4. Check Permission

```bash
curl -X POST http://localhost:8080/api/v1/roles/check-permission \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 123,
    "resource": "/farmers",
    "action": "write",
    "domain": "HUB001"
  }'
```

---

## Direct gRPC Testing

### Using grpcurl

```bash
# List all services
grpcurl -plaintext localhost:50051 list

# List methods for AuthService
grpcurl -plaintext localhost:50051 list auth.v1.AuthService

# Call Login
grpcurl -plaintext \
  -d '{
    "identifier": "john@example.com",
    "password": "SecurePass123"
  }' \
  localhost:50051 auth.v1.AuthService/Login

# Call with authentication
grpcurl -plaintext \
  -H "Authorization: Bearer $TOKEN" \
  localhost:50051 auth.v1.AuthService/GetProfile

# Call mobile register with device info
grpcurl -plaintext \
  -d '{
    "phone_number": "+84901234567",
    "otp_id": "uuid-1234",
    "pin": "123456",
    "name": "Test User",
    "device_info": {
      "device_id": "test-123",
      "device_type": "mobile"
    }
  }' \
  localhost:50051 mobile.v1.MobileAuthService/Register
```

---

## Error Handling Tests

### Test Invalid Credentials

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "john@example.com",
    "password": "WrongPassword"
  }'
```

**Expected:** 401 Unauthorized

### Test Expired Token

```bash
# Use old/expired token
curl http://localhost:8080/api/v1/auth/profile \
  -H "Authorization: Bearer expired_token"
```

**Expected:** 401 Unauthorized, "Token expired" message

### Test Rate Limiting (OTP)

```bash
# Send 6 OTP requests rapidly
for i in {1..6}; do
  curl -X POST http://localhost:8080/api/v1/mobile/send-register-otp \
    -H "Content-Type: application/json" \
    -d '{"phone_number": "+84901234567"}'
  sleep 1
done
```

**Expected:** 6th request returns 429 Too Many Requests

### Test Invalid OTP

```bash
curl -X POST http://localhost:8080/api/v1/mobile/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+84901234567",
    "otp_id": "uuid-1234",
    "otp_code": "000000"
  }'
```

**Expected:** 400 Bad Request, "Invalid OTP" message

---

## Performance Testing

### Load Test with k6

Create `load_test.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,           // 10 virtual users
  duration: '30s',   // Run for 30 seconds
};

export default function () {
  // Test login endpoint
  const payload = JSON.stringify({
    identifier: 'john@example.com',
    password: 'SecurePass123',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post('http://localhost:8080/api/v1/auth/login', payload, params);
  
  check(res, {
    'is status 200': (r) => r.status === 200,
    'has access_token': (r) => JSON.parse(r.body).data.access_token !== '',
  });

  sleep(1);
}
```

Run load test:

```bash
k6 run load_test.js
```

### Benchmark with Apache Bench

```bash
# Test login endpoint
ab -n 1000 -c 10 \
  -p login.json \
  -T application/json \
  http://localhost:8080/api/v1/auth/login

# Where login.json contains:
# {"identifier":"john@example.com","password":"SecurePass123"}
```

---

## Database Testing

### Check Data Integrity

```sql
-- Connect to test database
psql -U postgres -d centre_auth_test

-- Check accounts created during tests
SELECT id, type, identifier, source, is_ekyc, is_farmer 
FROM accounts 
WHERE is_deleted = FALSE
ORDER BY created_at DESC
LIMIT 10;

-- Check refresh tokens
SELECT account_id, expires_at, is_revoked 
FROM refresh_tokens 
WHERE account_id = 1
ORDER BY created_at DESC;

-- Check device sessions
SELECT account_id, device_type, device_name, last_active_at 
FROM device_sessions 
WHERE account_id = 1;

-- Check OTP verifications
SELECT phone, code, verified, expires_at 
FROM otp_verifications 
WHERE phone = '+84901234567'
ORDER BY created_at DESC;
```

### Cleanup Test Data

```sql
-- Delete test accounts
DELETE FROM accounts WHERE identifier LIKE '%@example.com';
DELETE FROM accounts WHERE identifier LIKE '+8490%';

-- Reset sequences
ALTER SEQUENCE accounts_id_seq RESTART WITH 1;
ALTER SEQUENCE users_id_seq RESTART WITH 1;
```

---

## Automated Test Scenarios

### Postman Collection

Import this collection for automated testing:

```json
{
  "info": {
    "name": "CAS API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth Flow",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "http://localhost:8080/api/v1/auth/register",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Test User\",\n  \"identifier\": \"test@example.com\",\n  \"password\": \"Test123\"\n}"
            },
            "header": [
              {"key": "Content-Type", "value": "application/json"}
            ]
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 200', function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "pm.test('Response has access_token', function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.data.access_token).to.exist;",
                  "    pm.environment.set('access_token', jsonData.data.access_token);",
                  "    pm.environment.set('refresh_token', jsonData.data.refresh_token);",
                  "});"
                ]
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## Test Coverage Goals

Target coverage by component:

- **Usecase Layer:** 80%+ coverage
- **Repository Layer:** 70%+ coverage
- **Handler Layer:** 60%+ coverage
- **Overall Project:** 70%+ coverage

Check current coverage:

```bash
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total
```

---

## Continuous Integration

### GitHub Actions Example

`.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: centre_auth_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.21'
    
    - name: Run tests
      run: go test -v -coverprofile=coverage.out ./...
      env:
        DATABASE_HOST: localhost
        REDIS_HOST: localhost
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.out
```

---

## Troubleshooting

### Common Issues

**Issue:** Database connection failed  
**Solution:** Check PostgreSQL is running and credentials are correct

```bash
psql -U postgres -d centre_auth_test -c "SELECT 1"
```

**Issue:** Redis connection failed  
**Solution:** Check Redis is running

```bash
redis-cli ping
```

**Issue:** gRPC reflection not enabled  
**Solution:** Ensure reflection is enabled in server.go:

```go
reflection.Register(grpcServer)
```

**Issue:** OTP not received  
**Solution:** Check Telegram bot configuration in config.yaml

**Issue:** Token validation fails  
**Solution:** Verify JWT secret keys match between services

---

## Navigation

### Documentation Home
- [Back to README](../../README.md) - Main documentation hub

### Related Documentation
- [Architecture Overview](../architecture/overview.md) - System design and components
- [API Reference](../api/api_reference.md) - Complete API documentation
- [Database Schema](../database/schema.md) - Data models and relationships
- [Deployment Guide](deployment_guide.md) - Production deployment

### Project Documentation
- [CHANGELOG](../../CHANGELOG.md) - Version history and updates
- [Port Allocation](../../../docs/PORT_ALLOCATION.md) - System-wide port assignments

**Version**: 1.0.0 | [Back to Top](#centre-auth-service-testing-guide)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-18 | Initial testing guide with comprehensive test scenarios |
