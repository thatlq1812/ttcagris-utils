# [TDD] Technical Design Document Title

| Version | Date | Author | Status |
| --- | --- | --- | --- |
| 1.0.0 | DD MMM YYYY | @Author Name | Draft |

**Status**: Draft | Under Review | Approved | Implemented

---

## 1. Overview

### 1.1 Purpose

Brief description of what this technical design aims to achieve.

### 1.2 Scope

What is included and excluded from this design.

### 1.3 Related Documents

- [SRS] Software Requirements Specification
- [ADR] Related Architecture Decisions
- **Jira Epic**: AGRIOS-XXX

---

## 2. Background

### 2.1 Current System

Description of existing system or component being modified.

### 2.2 Problem Statement

What technical challenges need to be solved?

### 2.3 Goals

- Goal 1: Improve performance by X%
- Goal 2: Reduce complexity
- Goal 3: Enable feature Y

---

## 3. Functional Requirements Summary

Brief summary referencing detailed requirements in SRS document.

### 3.1 Must Have (P0)

- Requirement 1
- Requirement 2

### 3.2 Should Have (P1)

- Requirement 3

### 3.3 Nice to Have (P2)

- Requirement 4

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Gateway   │────▶│   Service   │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  Database   │
                    └─────────────┘
```

### 4.2 Component Diagram

Detailed diagram showing all components and their interactions.

### 4.3 Deployment Architecture

How components are deployed across environments.

---

## 5. Detailed Design

### 5.1 Component A: [Component Name]

#### 5.1.1 Responsibility

What is this component responsible for?

#### 5.1.2 Interfaces

**Public APIs:**
```go
type UserService interface {
    CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error)
    GetUser(ctx context.Context, id string) (*User, error)
    UpdateUser(ctx context.Context, id string, req *UpdateUserRequest) (*User, error)
    DeleteUser(ctx context.Context, id string) error
}
```

**Dependencies:**
- Database: PostgreSQL
- Cache: Redis
- Message Queue: RabbitMQ

#### 5.1.3 Internal Structure

```
component-a/
├── handler/       # HTTP/gRPC handlers
├── service/       # Business logic
├── repository/    # Data access
└── domain/        # Domain models
```

### 5.2 Component B: [Component Name]

...

---

## 6. Data Model

### 6.1 Database Schema

#### 6.1.1 Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### 6.1.2 Products Table

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id UUID REFERENCES categories(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 6.2 Entity Relationships

```
users ──< ratings >── products
       1:N        N:1
```

### 6.3 Cache Strategy

**What to cache:**
- User sessions (TTL: 1 hour)
- Product catalog (TTL: 5 minutes)
- Category tree (TTL: 1 hour)

**Cache Keys:**
```
user:session:{user_id}
product:detail:{product_id}
category:tree:all
```

---

## 7. API Design

**Note**: For comprehensive API documentation, link to OpenAPI/Swagger specification file if available to avoid lengthy JSON examples in this document. Example: `See [OpenAPI Spec](../api/openapi.yaml) for complete API reference.`

### 7.1 REST Endpoints

#### 7.1.1 Create User

**Endpoint**: `POST /api/v1/users`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "createdAt": "2025-12-26T10:00:00Z"
}
```

**Errors**:
- 400: Invalid input
- 409: Email already exists

#### 7.1.2 Get User

**Endpoint**: `GET /api/v1/users/{id}`

**Response** (200 OK):
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

**Errors**:
- 404: User not found
- 401: Unauthorized

### 7.2 gRPC Services

#### 7.2.1 Service Definition

```protobuf
service UserService {
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc GetUser(GetUserRequest) returns (User);
  rpc UpdateUser(UpdateUserRequest) returns (User);
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);
}

message CreateUserRequest {
  string email = 1 [(buf.validate.field).string.email = true];
  string password = 2 [(buf.validate.field).string.min_len = 8];
  string name = 3 [(buf.validate.field).string.min_len = 1];
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  string role = 4;
  google.protobuf.Timestamp created_at = 5;
}
```

---

## 8. Security Design

### 8.1 Authentication

- **Method**: JWT tokens
- **Token Expiry**: 1 hour
- **Refresh Token**: 30 days
- **Storage**: HTTP-only cookies

### 8.2 Authorization

- **Model**: Role-Based Access Control (RBAC)
- **Roles**: Admin, User
- **Implementation**: Middleware checks user role before allowing access

### 8.3 Data Protection

- **Passwords**: bcrypt hashing (cost factor 12)
- **Sensitive Data**: Encrypted at rest using AES-256
- **API Keys**: Stored in HashiCorp Vault

### 8.4 Input Validation

- Use buf.validate for protobuf messages
- Sanitize all user inputs
- Parameterized queries to prevent SQL injection

---

## 9. Performance Considerations

### 9.1 Performance Requirements

From NFR section of SRS:
- P90 Latency ≤ 200ms
- Throughput: 1000 req/s
- Database query time < 50ms

### 9.2 Optimization Strategies

#### 9.2.1 Database Optimization

- Proper indexing on frequently queried columns
- Connection pooling (min: 10, max: 50)
- Read replicas for heavy read operations

#### 9.2.2 Caching Strategy

- Redis for session data
- In-memory cache for reference data
- Cache hit rate target: 80%

#### 9.2.3 Query Optimization

- Use EXPLAIN ANALYZE for slow queries
- Avoid N+1 query problems
- Use batch loading with DataLoader pattern

---

## 10. Error Handling

### 10.1 Error Code Convention

| Code | HTTP | gRPC | Description |
| --- | --- | --- | --- |
| ERR-001 | 400 | INVALID_ARGUMENT | Invalid input |
| ERR-002 | 401 | UNAUTHENTICATED | Authentication failed |
| ERR-003 | 403 | PERMISSION_DENIED | Insufficient permissions |
| ERR-004 | 404 | NOT_FOUND | Resource not found |
| ERR-005 | 409 | ALREADY_EXISTS | Resource conflict |
| ERR-500 | 500 | INTERNAL | Internal server error |

### 10.2 Error Response Format

```json
{
  "error": {
    "code": "ERR-001",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}
```

---

## 11. Testing Strategy

### 11.1 Unit Testing

- **Target Coverage**: 80%
- **Framework**: Go testing package
- **Mocking**: Mockery for interfaces

### 11.2 Integration Testing

- Test API endpoints
- Test database interactions
- Test external service integrations

### 11.3 Performance Testing

- Load testing with k6
- Stress testing to find breaking point
- Soak testing for memory leaks

---

## 12. Monitoring and Observability

### 12.1 Metrics

**Application Metrics:**
- Request rate
- Error rate
- Response time (P50, P90, P99)

**Infrastructure Metrics:**
- CPU usage
- Memory usage
- Database connections

### 12.2 Logging

**Log Levels:**
- ERROR: System errors requiring attention
- WARN: Potential issues
- INFO: Normal operation events
- DEBUG: Detailed diagnostic information

**Structured Logging:**
```go
logger.Infow("user created",
    "userId", user.ID,
    "email", user.Email,
    "duration", time.Since(start),
)
```

### 12.3 Distributed Tracing

- OpenTelemetry for trace collection
- Jaeger for trace visualization
- Trace all inter-service calls

---

## 13. Deployment Plan

### 13.1 Deployment Strategy

- **Strategy**: Blue-Green Deployment
- **Rollback Plan**: Keep previous version for 24 hours
- **Monitoring Period**: 48 hours before considering stable

### 13.2 Migration Steps

#### Phase 1: Preparation
1. Deploy new version alongside old
2. Run both versions in parallel
3. Route 10% traffic to new version

#### Phase 2: Gradual Rollout
1. Monitor metrics for anomalies
2. Gradually increase traffic to 50%
3. If stable, route 100% to new version

#### Phase 3: Cleanup
1. Monitor for 24 hours
2. Decommission old version
3. Clean up old resources

---

## 14. Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- |
| Database migration fails | Medium | High | Test on staging, have rollback script |
| Performance regression | Low | High | Load test before deployment |
| Breaking API changes | Medium | High | Version APIs, maintain backward compatibility |

---

## 15. Dependencies

### 15.1 Internal Dependencies

- User Service v2.0
- Auth Service v1.5
- Database migration scripts

### 15.2 External Dependencies

- Redis 7+
- PostgreSQL 17+
- RabbitMQ 3.12+

---

## 16. Open Questions

- [ ] Question 1: How to handle concurrent updates?
- [ ] Question 2: What is maximum file upload size?
- [ ] Question 3: Should we support bulk operations?

---

## 17. Appendix

### 17.1 Glossary

| Term | Definition |
| --- | --- |
| JWT | JSON Web Token |
| RBAC | Role-Based Access Control |
| P90 | 90th percentile |

### 17.2 References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [gRPC Best Practices](https://grpc.io/docs/guides/performance/)

---

## 18. Approval

**Reviewed By**:
- [ ] Tech Lead: @Name
- [ ] Senior Backend Engineer: @Name
- [ ] DevOps Lead: @Name

**Approved By**: @Tech Lead
**Approval Date**: DD MMM YYYY
