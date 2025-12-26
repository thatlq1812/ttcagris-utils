# [TDD] Centre Auth Service - Technical Design Document

| Version | Date | Author | Status |
| --- | --- | --- | --- |
| 1.0.0 | 26 Dec 2025 | That Le | Approved |

**Status**: Approved

---

## 1. Overview

### 1.1 Purpose

This document describes the technical design and implementation details for the Centre Auth Service (CAS). It provides guidance for developers implementing, maintaining, and extending the service.

### 1.2 Scope

This document covers:
- System architecture and components
- Data models and database schema
- API design and gRPC services
- Authentication and authorization implementation
- Integration patterns with external services

### 1.3 Related Documents

- [SRS] Centre Auth Service - Software Requirements Specification
- [SRS] API Gateway
- **Jira Epic**: AGRIOS-CAS

---

## 2. Background

### 2.1 Current System

CAS is a production microservice handling all authentication and identity management for the AgriOS Platform. It processes approximately 10,000 authentication requests daily and manages 50,000+ user accounts.

### 2.2 Problem Statement

The service must:
- Handle high-volume authentication requests with low latency
- Integrate multiple authentication providers (email, phone, Azure SSO)
- Manage complex user hierarchies (accounts, farmers, suppliers)
- Ensure security compliance for agricultural financial services

### 2.3 Goals

- P90 latency < 200ms for authentication endpoints
- Support 500 concurrent users
- Secure storage of sensitive identity data
- Extensible architecture for future authentication methods

---

## 3. Functional Requirements Summary

### 3.1 Must Have (P0)

- Email/password authentication
- Phone/OTP authentication
- JWT token management
- Account CRUD operations
- RBAC enforcement

### 3.2 Should Have (P1)

- Azure SSO integration
- eKYC integration
- Device session management
- Audit logging

### 3.3 Nice to Have (P2)

- Multi-factor authentication
- Biometric authentication
- Social login (Google, Facebook)

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
                                    ┌─────────────────────────────┐
                                    │      External Clients       │
                                    │   (Mobile App, Web Portal)  │
                                    └─────────────┬───────────────┘
                                                  │
                                                  ▼
                              ┌───────────────────────────────────────┐
                              │           API Gateway                 │
                              │      (REST → gRPC Translation)        │
                              │           Port: 8080                  │
                              └───────────────────┬───────────────────┘
                                                  │ gRPC
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Centre Auth Service (CAS)                          │
│                              Port: 50051 (gRPC)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ AuthService  │  │AccountService│  │ UserService  │  │ RoleService  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │            │
│  ┌──────┴─────────────────┴─────────────────┴─────────────────┴──────┐     │
│  │                         Use Cases Layer                           │     │
│  └──────┬─────────────────┬─────────────────┬─────────────────┬──────┘     │
│         │                 │                 │                 │            │
│  ┌──────┴─────────────────┴─────────────────┴─────────────────┴──────┐     │
│  │                       Repository Layer                            │     │
│  └───────────────────────────────┬───────────────────────────────────┘     │
└──────────────────────────────────┼──────────────────────────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │  PostgreSQL │         │    Redis    │         │ Azure Blob  │
    │   Database  │         │    Cache    │         │   Storage   │
    └─────────────┘         └─────────────┘         └─────────────┘
```

### 4.2 Component Diagram

```
centre-auth-service/
├── cmd/app/main.go              # Application entry point
├── config/
│   ├── config.go                # Configuration struct
│   └── config.yaml              # Configuration file
├── internal/
│   ├── api/                     # HTTP handlers (legacy)
│   ├── cmd/                     # Wire dependency injection
│   ├── domain/                  # Domain models
│   ├── grpc/                    # gRPC service implementations
│   ├── repository/              # Data access layer
│   ├── services/                # External service clients
│   ├── usecase/                 # Business logic
│   └── util/                    # Utility functions
├── migrations/                  # SQL migration files
├── pkg/                         # Reusable packages
│   ├── jwt/                     # JWT management
│   ├── casbin/                  # RBAC implementation
│   ├── storage/                 # Azure Blob client
│   └── grpcclient/              # External gRPC clients
└── proto/                       # Proto definitions (local)
```

### 4.3 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   CAS Pod 1     │  │   CAS Pod 2     │   (Replicas)     │
│  │   :50051        │  │   :50051        │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                            │
│           └──────────┬─────────┘                            │
│                      ▼                                      │
│           ┌─────────────────┐                               │
│           │  Service (LB)   │                               │
│           │   :50051        │                               │
│           └─────────────────┘                               │
└─────────────────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      ▼               ▼               ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│PostgreSQL │  │   Redis   │  │Azure Blob │
│  Managed  │  │  Cluster  │  │  Storage  │
└───────────┘  └───────────┘  └───────────┘
```

---

## 5. Detailed Design

### 5.1 Authentication Module

#### 5.1.1 Responsibility

Handles user authentication via multiple providers and manages JWT tokens.

#### 5.1.2 Interfaces

```go
type AuthUsecase interface {
    Login(ctx context.Context, req *domain.LoginRequest) (*domain.LoginResponse, error)
    Register(ctx context.Context, req *domain.RegisterRequest) (*domain.Account, error)
    RefreshToken(ctx context.Context, refreshToken string) (*domain.RefreshTokenResponse, error)
    RevokeToken(ctx context.Context, req *domain.RevokeTokenRequest) error
    VerifyToken(ctx context.Context, token string) (*domain.AuthContext, error)
    AzureCallback(ctx context.Context, req *domain.AzureCallbackRequest) (*domain.LoginResponse, error)
}
```

#### 5.1.3 Authentication Flow

```
┌──────────┐     ┌────────────┐     ┌──────────────┐     ┌──────────┐
│  Client  │────▶│ AuthServer │────▶│ AuthUsecase  │────▶│Repository│
└──────────┘     └────────────┘     └──────────────┘     └──────────┘
     │                 │                   │                   │
     │  LoginRequest   │                   │                   │
     │────────────────▶│                   │                   │
     │                 │   Validate        │                   │
     │                 │──────────────────▶│                   │
     │                 │                   │   Find Account    │
     │                 │                   │──────────────────▶│
     │                 │                   │   Account         │
     │                 │                   │◀──────────────────│
     │                 │                   │                   │
     │                 │   Verify Password │                   │
     │                 │◀──────────────────│                   │
     │                 │                   │                   │
     │                 │   Generate Tokens │                   │
     │                 │◀──────────────────│                   │
     │                 │                   │                   │
     │  LoginResponse  │                   │                   │
     │◀────────────────│                   │                   │
```

#### 5.1.4 JWT Token Structure

**Access Token Claims:**
```json
{
  "account_id": 12345,
  "account_type": "phone",
  "role": "farmer",
  "name": "Nguyen Van A",
  "exp": 1735257600,
  "iat": 1735254000
}
```

**Token Configuration:**
| Setting | Web | Mobile |
| --- | --- | --- |
| Secret Key | `secret_key_web` | `secret_key_app` |
| Access Token TTL | 1 hour | 1 hour |
| Refresh Token TTL | 7 days | 30 days |
| Algorithm | HS256 | HS256 |

### 5.2 Account Module

#### 5.2.1 Responsibility

Manages account lifecycle including creation, updates, and relationships.

#### 5.2.2 Interfaces

```go
type AccountUsecase interface {
    Create(ctx context.Context, req *domain.CreateAccountRequest) (*domain.Account, error)
    GetByID(ctx context.Context, id int64) (*domain.Account, error)
    GetByIdentifier(ctx context.Context, identifier string) (*domain.Account, error)
    List(ctx context.Context, query *pageable.Query) ([]*domain.Account, int64, error)
    Update(ctx context.Context, id int64, req *domain.UpdateAccountRequest) (*domain.Account, error)
    Delete(ctx context.Context, id int64) error
}
```

#### 5.2.3 Account Code Generation

Each account receives a unique 8-character code using nanoid:

```go
import gonanoid "github.com/matoous/go-nanoid/v2"

func generateAccountCode() (string, error) {
    // Alphabet: 0-9, A-Z (uppercase only, no ambiguous chars)
    alphabet := "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    return gonanoid.Generate(alphabet, 8)
}
```

### 5.3 RBAC Module (Casbin)

#### 5.3.1 Responsibility

Enforces role-based access control on all protected endpoints.

#### 5.3.2 Policy Model

```
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
```

#### 5.3.3 Role Hierarchy

```
           admin
          /     \
    supervisor  approver
        |
      staff
       / \
  farmer  supplier
```

#### 5.3.4 Permission Enforcement

```go
// gRPC Interceptor for permission checking
func (i *PermissionInterceptor) UnaryInterceptor(
    ctx context.Context,
    req interface{},
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (interface{}, error) {
    // Extract method name: /auth.v1.AccountService/GetAccount
    method := info.FullMethod
    
    // Get account from context (set by auth interceptor)
    accountID := getAccountIDFromContext(ctx)
    
    // Check permission
    allowed, err := i.enforcer.Enforce(accountID, method, "execute")
    if !allowed {
        return nil, status.Error(codes.PermissionDenied, "access denied")
    }
    
    return handler(ctx, req)
}
```

### 5.4 eKYC Integration Module

#### 5.4.1 Responsibility

Integrates with external IED (Identity Electronic Verification) service for KYC operations.

#### 5.4.2 Integration Flow

```
┌──────────┐     ┌────────────┐     ┌──────────────┐     ┌──────────┐
│  Client  │────▶│ EkycServer │────▶│ EkycUsecase  │────▶│IED Service│
└──────────┘     └────────────┘     └──────────────┘     └──────────┘
     │                 │                   │                   │
     │ ID Card Images  │                   │                   │
     │────────────────▶│                   │                   │
     │                 │   Process OCR     │                   │
     │                 │──────────────────▶│                   │
     │                 │                   │   OCR Request     │
     │                 │                   │──────────────────▶│
     │                 │                   │   OCR Response    │
     │                 │                   │◀──────────────────│
     │                 │                   │                   │
     │ Selfie Image    │                   │                   │
     │────────────────▶│                   │                   │
     │                 │   Liveness Check  │                   │
     │                 │──────────────────▶│                   │
     │                 │                   │   Liveness Req    │
     │                 │                   │──────────────────▶│
     │                 │                   │   Liveness Resp   │
     │                 │                   │◀──────────────────│
     │                 │                   │                   │
     │                 │   Face Compare    │                   │
     │                 │──────────────────▶│                   │
     │                 │                   │   Compare Req     │
     │                 │                   │──────────────────▶│
     │                 │                   │   Compare Resp    │
     │                 │                   │◀──────────────────│
     │                 │                   │                   │
     │ eKYC Complete   │                   │                   │
     │◀────────────────│                   │                   │
```

#### 5.4.3 Data Storage

eKYC images are encrypted before storage:

```go
// Encryption for sensitive image data
func encryptImageData(data []byte, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    
    nonce := make([]byte, gcm.NonceSize())
    if _, err := rand.Read(nonce); err != nil {
        return nil, err
    }
    
    return gcm.Seal(nonce, nonce, data, nil), nil
}
```

---

## 6. Data Model

### 6.1 Database Schema

#### 6.1.1 Accounts Table

```sql
CREATE TABLE accounts (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(8) UNIQUE NOT NULL,
    type VARCHAR(20) NOT NULL,        -- 'email', 'phone', 'sso'
    identifier VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255),
    provider VARCHAR(50),              -- For SSO: 'azure'
    source VARCHAR(20) NOT NULL,       -- 'app', 'web'
    is_ekyc BOOLEAN DEFAULT FALSE,
    is_frm_farmer BOOLEAN DEFAULT FALSE,
    is_farmer BOOLEAN DEFAULT FALSE,
    is_supplier BOOLEAN DEFAULT FALSE,
    is_active_farmer BOOLEAN DEFAULT FALSE,
    is_active_supplier BOOLEAN DEFAULT FALSE,
    is_form BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_deactive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_accounts_identifier ON accounts(identifier);
CREATE INDEX idx_accounts_code ON accounts(code);
CREATE INDEX idx_accounts_type ON accounts(type);
```

#### 6.1.2 Users Table

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT UNIQUE REFERENCES accounts(id),
    name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    date_of_birth DATE,
    gender VARCHAR(20),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_account_id ON users(account_id);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_email ON users(email);
```

#### 6.1.3 Farmers Table

```sql
CREATE TABLE farmers (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL UNIQUE REFERENCES accounts(id),
    customer_code TEXT,
    avarta_url TEXT,
    investment_area TEXT,
    agricultural_officer TEXT,
    area NUMERIC(10,2),
    cultivated_area JSONB,
    crop_types TEXT[],
    investment_zone TEXT,
    investment_programs TEXT[],
    customer_type TEXT,
    customer_group TEXT,
    img_front_url TEXT,
    img_back_url TEXT,
    status TEXT,
    is_skip BOOLEAN DEFAULT FALSE,
    is_contact BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_farmers_account_id ON farmers(account_id);
CREATE INDEX idx_farmers_status ON farmers(status);
CREATE INDEX idx_farmers_customer_code ON farmers(customer_code);
```

#### 6.1.4 Suppliers Table

```sql
CREATE TABLE suppliers (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES accounts(id),
    company_name TEXT,
    company_address JSONB,
    business_field TEXT[],
    business_id TEXT,
    tax_code TEXT,
    representative_name TEXT,
    representative_position TEXT,
    representative_address JSONB,
    representative_card_number TEXT,
    img_back BYTEA,                    -- Encrypted
    img_front BYTEA,                   -- Encrypted
    data_url JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    denied_reason TEXT,
    name TEXT,
    operation_area JSONB,
    activity_type TEXT,
    crop_type_supported TEXT[],
    cultivation_service_type TEXT[],
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_suppliers_account_id ON suppliers(account_id);
CREATE INDEX idx_suppliers_status ON suppliers(status);
```

#### 6.1.5 eKYC Table

```sql
CREATE TABLE ekycs (
    id SERIAL PRIMARY KEY,
    account_id BIGINT REFERENCES accounts(id),
    img TEXT,
    img_back TEXT,
    img_front TEXT,
    img_near TEXT,
    img_far TEXT,
    image_far BYTEA,                   -- Encrypted
    image_front BYTEA,                 -- Encrypted
    image_back BYTEA,                  -- Encrypted
    mrz TEXT,
    face_image TEXT,
    card_number TEXT,
    date_of_birth TEXT,
    issue_date TEXT,
    previous_number TEXT,
    name TEXT,
    sex TEXT,
    nationality TEXT,
    nation TEXT,
    religion TEXT,
    hometown TEXT,
    address TEXT,
    character TEXT,
    expired_date TEXT,
    father_name TEXT,
    mother_name TEXT,
    partner_name TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ekycs_account_id ON ekycs(account_id);
CREATE INDEX idx_ekycs_card_number ON ekycs(card_number);
```

### 6.2 Entity Relationships

```
┌─────────────┐
│   Account   │
│─────────────│
│ id (PK)     │
│ code        │
│ type        │
│ identifier  │
└──────┬──────┘
       │
       │ 1:1
       ▼
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │
│ account_id  │◄─────┐
│ name        │      │
└─────────────┘      │
                     │ 1:0..1
┌─────────────┐      │
│   Farmer    │──────┘
│─────────────│
│ id (PK)     │
│ account_id  │
│ area        │
└─────────────┘

┌─────────────┐
│  Supplier   │──────┐
│─────────────│      │
│ id (PK)     │      │ 1:0..1
│ account_id  │◄─────┘
│ company_name│
└─────────────┘
```

---

## 7. API Design

### 7.1 gRPC Services

#### 7.1.1 AuthService

```protobuf
service AuthService {
  rpc Login(LoginRequest) returns (LoginResponse);
  rpc Register(RegisterRequest) returns (RegisterResponse);
  rpc RefreshToken(RefreshTokenRequest) returns (RefreshTokenResponse);
  rpc RevokeToken(RevokeTokenRequest) returns (RevokeTokenResponse);
  rpc VerifyToken(VerifyTokenRequest) returns (VerifyTokenResponse);
  rpc AzureCallback(AzureCallbackRequest) returns (LoginResponse);
}
```

#### 7.1.2 AccountService

```protobuf
service AccountService {
  rpc CreateAccount(CreateAccountRequest) returns (Account);
  rpc GetAccount(GetAccountRequest) returns (Account);
  rpc ListAccounts(ListAccountsRequest) returns (ListAccountsResponse);
  rpc UpdateAccount(UpdateAccountRequest) returns (Account);
  rpc DeleteAccount(DeleteAccountRequest) returns (DeleteAccountResponse);
}
```

### 7.2 Error Handling

| gRPC Code | HTTP Code | Description |
| --- | --- | --- |
| OK | 200 | Success |
| INVALID_ARGUMENT | 400 | Validation error |
| UNAUTHENTICATED | 401 | Missing/invalid token |
| PERMISSION_DENIED | 403 | Not authorized |
| NOT_FOUND | 404 | Resource not found |
| ALREADY_EXISTS | 409 | Duplicate resource |
| INTERNAL | 500 | Server error |

---

## 8. Security Design

### 8.1 Authentication Flow

1. Client sends credentials
2. Server validates credentials
3. Server generates JWT tokens
4. Client stores tokens securely
5. Client includes token in subsequent requests
6. Server validates token on each request

### 8.2 Token Blacklist

Revoked tokens are stored in Redis with TTL matching token expiry:

```go
type TokenBlacklist struct {
    redis *redis.Client
}

func (tb *TokenBlacklist) Add(tokenID string, expiry time.Duration) error {
    return tb.redis.Set(ctx, "blacklist:"+tokenID, "1", expiry).Err()
}

func (tb *TokenBlacklist) IsBlacklisted(tokenID string) (bool, error) {
    result, err := tb.redis.Exists(ctx, "blacklist:"+tokenID).Result()
    return result > 0, err
}
```

### 8.3 Service-to-Service Authentication

Two mechanisms supported:
1. **API Key**: Simple key-based authentication for internal services
2. **Signature**: HMAC-based request signing for external integrations

---

## 9. Integration Points

### 9.1 External Services

| Service | Purpose | Protocol |
| --- | --- | --- |
| API Gateway | REST to gRPC translation | gRPC |
| Notification Service | Push notifications | gRPC |
| Hub Service | Hub data retrieval | gRPC |
| IED Service | eKYC verification | HTTPS |
| Azure AD | SSO authentication | OAuth 2.0 |
| Azure Blob | File storage | HTTPS |

### 9.2 Configuration for External Services

```yaml
services:
  notification:
    grpc_addr: "noti-service:9012"
  hub:
    grpc_addr: "hub-service:50052"

ekyc:
  base_url: "https://ied-api.example.com"
  api_key: "${IED_API_KEY}"

azure:
  client_id: "${AZURE_CLIENT_ID}"
  client_secret: "${AZURE_CLIENT_SECRET}"
  token_url: "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
```

---

## 10. Observability

### 10.1 Logging

Structured logging with Zap:

```go
aglog.Infow("user authenticated",
    "account_id", accountID,
    "type", loginType,
    "duration_ms", duration.Milliseconds(),
)
```

### 10.2 Metrics

Key metrics exposed:
- `cas_auth_requests_total` - Authentication request counter
- `cas_auth_latency_seconds` - Authentication latency histogram
- `cas_active_sessions` - Current active session gauge
- `cas_token_validations_total` - Token validation counter

### 10.3 Health Checks

```go
// Health check endpoint
GET /health

// Response
{
  "status": "ok",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

---

## 11. Deployment

### 11.1 Environment Variables

| Variable | Description | Required |
| --- | --- | --- |
| `DATABASE_HOST` | PostgreSQL host | Yes |
| `DATABASE_PASSWORD` | PostgreSQL password | Yes |
| `REDIS_ADDRESS` | Redis address | Yes |
| `JWT_SECRET_KEY_WEB` | JWT secret for web | Yes |
| `JWT_SECRET_KEY_APP` | JWT secret for mobile | Yes |
| `AZURE_CLIENT_ID` | Azure AD client ID | No |
| `IED_API_KEY` | eKYC API key | No |

### 11.2 Docker Build

```dockerfile
FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o bin/app cmd/app/main.go

FROM alpine:latest
COPY --from=builder /app/bin/app /app
COPY --from=builder /app/config /config
EXPOSE 50051 4000
CMD ["/app", "api"]
```

### 11.3 Kubernetes Resources

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: centre-auth-service
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: cas
        image: cas:latest
        ports:
        - containerPort: 50051
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 12. Testing Strategy

### 12.1 Unit Tests

```bash
make test
```

Test coverage target: 80%

### 12.2 Integration Tests

```bash
# Run with test database
DATABASE_HOST=localhost make test-integration
```

### 12.3 Load Testing

```bash
# Using grpcurl for load testing
ghz --insecure \
    --proto proto/auth/v1/auth.proto \
    --call auth.v1.AuthService.Login \
    --data '{"type":"email","identifier":"test@example.com","password":"password"}' \
    --connections=50 \
    --concurrency=100 \
    --duration=60s \
    localhost:50051
```

---

## 13. Migration Strategy

### 13.1 Automatic Migrations

Migrations run automatically on service startup:

```go
func RunMigrations(db *gorm.DB) error {
    return db.AutoMigrate(
        &domain.Account{},
        &domain.User{},
        &domain.Farmer{},
        &domain.Supplier{},
        &domain.Ekyc{},
    )
}
```

### 13.2 Manual Migrations

For complex schema changes:

```bash
make migrate-up
```

---

## 14. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Database connection failure | High | Connection pooling, retry logic |
| Redis unavailable | Medium | Graceful degradation, local cache |
| Token secret leak | Critical | Vault integration, key rotation |
| eKYC service down | Medium | Circuit breaker, queue for retry |

---

## 15. Future Considerations

- Multi-factor authentication (MFA)
- Social login providers
- Passwordless authentication
- Biometric authentication for mobile
- Enhanced audit logging with event sourcing
