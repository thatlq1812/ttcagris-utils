# [SRS] Centre Auth Service - Software Requirements Specification

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| 1.0.0 | 26 Dec 2025 | That Le | Initial document |

**Status**: Active

---

## 1. Introduction

### 1.1 Purpose

This document defines the software requirements for the Centre Auth Service (CAS), the centralized authentication and authorization microservice for the AgriOS Platform. It serves as a reference for development, testing, and stakeholder alignment.

### 1.2 Scope

This document applies to:
- Authentication services (login, logout, token management)
- Account management (CRUD operations)
- User profile management
- Farmer and supplier profile management
- Role-based access control (RBAC)
- eKYC identity verification integration
- Device session management

This document does NOT cover:
- API Gateway routing (see API Gateway SRS)
- Notification delivery (see Notification Service SRS)
- Business logic for farming operations (see Supplier Service SRS)

### 1.3 Target Audience

- Product Owner
- Backend Developer
- Frontend / Mobile Developer
- QC / Tester
- DevOps Engineer

### 1.4 Related Documents

- [TDD] Technical Design Document - CAS
- [SRS] API Gateway
- [SRS] Notification Service

---

## 2. System Overview

### 2.1 Architecture

CAS is a gRPC-based microservice following Clean Architecture with CQRS patterns. It exposes gRPC endpoints on port 50051 and optional HTTP endpoints on port 4000.

### 2.2 Assumptions and Constraints

**Assumptions:**
- Users have unique phone numbers or email addresses
- Azure AD is available for SSO authentication
- External eKYC provider (IED) is accessible

**Constraints:**
- Must use existing PostgreSQL database
- Must integrate with existing Redis cluster
- Must follow proto-first design from Core repository

---

## 3. Business Requirements

### BR-001: Multi-Channel Authentication

- **Description**: System must support authentication via email, phone (OTP), and SSO (Azure AD)
- **Priority**: High
- **Source**: Product Owner
- **Rationale**: Users access the platform from multiple channels (web, mobile) with different authentication preferences

### BR-002: Identity Verification

- **Description**: System must verify user identity through eKYC (electronic Know Your Customer) process
- **Priority**: High
- **Source**: Regulatory / Legal
- **Rationale**: Compliance with agricultural financial regulations requires identity verification

### BR-003: Role-Based Access Control

- **Description**: System must control access to resources based on user roles
- **Priority**: High
- **Source**: Security Requirements
- **Rationale**: Different user types (admin, farmer, supplier) require different access levels

### BR-004: Account Types

- **Description**: System must support multiple account types: Farmer and Supplier
- **Priority**: High
- **Source**: Product Owner
- **Rationale**: Platform serves both agricultural producers and service providers

### BR-005: Session Management

- **Description**: System must track and manage device sessions for security
- **Priority**: Medium
- **Source**: Security Requirements
- **Rationale**: Enable users to view and revoke active sessions

---

## 4. Functional Requirements

### 4.1 Authentication

#### FR-A01: User Login

- **Description**: System must authenticate users with valid credentials
- **Input**: 
  - type: `email` | `phone` | `sso`
  - identifier: email address, phone number, or SSO token
  - password: user password (for email/phone)
  - device_info: optional device information
- **Output**: 
  - access_token: JWT access token
  - refresh_token: JWT refresh token
  - user profile information
- **Acceptance Criteria**:
  - [ ] Valid credentials return tokens
  - [ ] Invalid credentials return 401 Unauthorized
  - [ ] Deactivated accounts cannot login
  - [ ] Device session is created on successful login

#### FR-A02: User Registration

- **Description**: System must allow new users to register
- **Input**: 
  - type: `email` | `phone`
  - identifier: email or phone number
  - password: minimum 8 characters
  - name: optional user name
- **Output**: Account created with associated user profile
- **Acceptance Criteria**:
  - [ ] Duplicate identifier returns error
  - [ ] Password is securely hashed
  - [ ] User profile is created

#### FR-A03: Token Refresh

- **Description**: System must issue new access token using valid refresh token
- **Input**: refresh_token
- **Output**: New access_token and refresh_token
- **Acceptance Criteria**:
  - [ ] Valid refresh token returns new tokens
  - [ ] Expired refresh token returns 401
  - [ ] Old refresh token is invalidated

#### FR-A04: Token Revocation

- **Description**: System must invalidate tokens on logout
- **Input**: access_token and/or refresh_token
- **Output**: Tokens invalidated
- **Acceptance Criteria**:
  - [ ] Revoked tokens cannot be used
  - [ ] Device session is removed

#### FR-A05: Azure SSO Login

- **Description**: System must authenticate users via Azure AD
- **Input**: 
  - code: OAuth authorization code
  - redirect_uri: callback URL
- **Output**: Tokens and user profile
- **Acceptance Criteria**:
  - [ ] Valid Azure code returns tokens
  - [ ] Account is created if not exists
  - [ ] Profile syncs from Azure

#### FR-A06: OTP Verification

- **Description**: System must verify phone number via OTP
- **Input**: phone number, OTP code
- **Output**: Verification status
- **Acceptance Criteria**:
  - [ ] Valid OTP within time limit succeeds
  - [ ] Invalid OTP returns error
  - [ ] OTP expires after configured duration

### 4.2 Account Management

#### FR-B01: Create Account

- **Description**: System must create new accounts with associated profiles
- **Input**: 
  - identifier: email or phone
  - password: user password
  - user: user profile data
  - farmer: farmer profile (optional)
  - supplier: supplier profile (optional)
- **Output**: Created account with relationships
- **Acceptance Criteria**:
  - [ ] Account code is generated (8 characters)
  - [ ] Source is set based on type
  - [ ] Related profiles are created

#### FR-B02: Get Account

- **Description**: System must retrieve account details
- **Input**: account_id
- **Output**: Account with related profiles
- **Acceptance Criteria**:
  - [ ] Returns complete account data
  - [ ] Includes user, farmer, supplier if exist
  - [ ] Deleted accounts are not returned

#### FR-B03: List Accounts

- **Description**: System must list accounts with filtering and pagination
- **Input**: 
  - page, size: pagination
  - filters: field-based filters
- **Output**: Paginated list of accounts
- **Acceptance Criteria**:
  - [ ] Pagination works correctly
  - [ ] Filters apply correctly
  - [ ] Soft-deleted excluded by default

#### FR-B04: Update Account

- **Description**: System must update account information
- **Input**: account_id, update fields
- **Output**: Updated account
- **Acceptance Criteria**:
  - [ ] Only provided fields are updated
  - [ ] Timestamps are updated
  - [ ] Audit log is created

#### FR-B05: Delete Account (Soft)

- **Description**: System must soft-delete accounts
- **Input**: account_id
- **Output**: Deletion confirmation
- **Acceptance Criteria**:
  - [ ] is_deleted flag is set
  - [ ] Account cannot login after deletion
  - [ ] Related profiles are soft-deleted

### 4.3 User Profile Management

#### FR-C01: Get User Profile

- **Description**: Retrieve user profile by ID or account ID
- **Input**: user_id or account_id
- **Output**: User profile data
- **Acceptance Criteria**:
  - [ ] Returns complete profile
  - [ ] Includes linked account info

#### FR-C02: Update User Profile

- **Description**: Update user profile information
- **Input**: user_id, profile fields (name, phone, email, address, date_of_birth, gender)
- **Output**: Updated profile
- **Acceptance Criteria**:
  - [ ] Partial updates supported
  - [ ] Validation applied
  - [ ] Timestamps updated

#### FR-C03: Change Password

- **Description**: User can change their password
- **Input**: current_password, new_password
- **Output**: Success confirmation
- **Acceptance Criteria**:
  - [ ] Current password verified
  - [ ] New password meets requirements (min 8 chars)
  - [ ] All sessions optionally invalidated

### 4.4 Farmer Management

#### FR-D01: Create Farmer Profile

- **Description**: Create farmer profile linked to account
- **Input**: account_id, farmer details (customer_code, area, crop_types, etc.)
- **Output**: Created farmer profile
- **Acceptance Criteria**:
  - [ ] Links to existing account
  - [ ] Account.is_farmer set to true
  - [ ] Farmer hub assigned if applicable

#### FR-D02: Get Farmer

- **Description**: Retrieve farmer profile
- **Input**: farmer_id or account_id
- **Output**: Farmer profile with related data
- **Acceptance Criteria**:
  - [ ] Returns complete farmer data
  - [ ] Includes parcel lands if exists

#### FR-D03: List Farmers

- **Description**: List farmers with filtering
- **Input**: pagination, filters (status, customer_type, area range)
- **Output**: Paginated farmer list
- **Acceptance Criteria**:
  - [ ] Filters by status work
  - [ ] Filters by agricultural_officer work
  - [ ] Includes account info

#### FR-D04: Update Farmer

- **Description**: Update farmer profile
- **Input**: farmer_id, update fields
- **Output**: Updated farmer
- **Acceptance Criteria**:
  - [ ] Partial updates work
  - [ ] Status transitions validated

### 4.5 Supplier Management

#### FR-E01: Create Supplier Profile

- **Description**: Create supplier profile linked to account
- **Input**: account_id, supplier details (company_name, business_field, tax_code, etc.)
- **Output**: Created supplier profile
- **Acceptance Criteria**:
  - [ ] Links to existing account
  - [ ] Account.is_supplier set to true
  - [ ] Initial status is 'pending'

#### FR-E02: Get Supplier

- **Description**: Retrieve supplier profile
- **Input**: supplier_id or account_id
- **Output**: Supplier profile
- **Acceptance Criteria**:
  - [ ] Returns complete supplier data
  - [ ] Includes business field info

#### FR-E03: List Suppliers

- **Description**: List suppliers with filtering
- **Input**: pagination, filters (status, activity_type, business_field)
- **Output**: Paginated supplier list
- **Acceptance Criteria**:
  - [ ] Filter by status works
  - [ ] Filter by activity_type works

#### FR-E04: Update Supplier Status

- **Description**: Approve or deny supplier applications
- **Input**: supplier_id, status, denied_reason (if denied)
- **Output**: Updated supplier
- **Acceptance Criteria**:
  - [ ] Status transitions: pending -> approved/denied
  - [ ] Denied requires reason
  - [ ] Account.is_active_supplier updated

### 4.6 Role and Permission Management

#### FR-F01: List Roles

- **Description**: Retrieve all available roles
- **Input**: None
- **Output**: List of roles
- **Acceptance Criteria**:
  - [ ] Returns all active roles

#### FR-F02: Assign Role to User

- **Description**: Assign role to user account
- **Input**: account_id, role_id
- **Output**: Role assignment
- **Acceptance Criteria**:
  - [ ] Role is assigned via Casbin
  - [ ] User permissions updated

#### FR-F03: Check Permission

- **Description**: Verify if user has permission for action
- **Input**: account_id, resource, action
- **Output**: Boolean permission status
- **Acceptance Criteria**:
  - [ ] Returns true if permitted
  - [ ] Returns false if not permitted

### 4.7 eKYC Integration

#### FR-G01: OCR ID Card

- **Description**: Extract information from ID card image
- **Input**: ID card image (front and back)
- **Output**: Extracted data (name, card_number, date_of_birth, address, etc.)
- **Acceptance Criteria**:
  - [ ] Front card data extracted
  - [ ] Back card data extracted
  - [ ] Confidence score returned

#### FR-G02: Face Liveness Check

- **Description**: Verify user is a real person
- **Input**: Selfie image/video
- **Output**: Liveness status
- **Acceptance Criteria**:
  - [ ] Detects live face
  - [ ] Rejects photos of photos
  - [ ] Returns confidence score

#### FR-G03: Face Comparison

- **Description**: Compare selfie with ID card photo
- **Input**: Selfie image, ID card face image
- **Output**: Match status and similarity score
- **Acceptance Criteria**:
  - [ ] Returns similarity percentage
  - [ ] Threshold configurable

#### FR-G04: Complete eKYC

- **Description**: Mark eKYC as complete
- **Input**: account_id, ekyc_data
- **Output**: Updated account with is_ekyc = true
- **Acceptance Criteria**:
  - [ ] Ekyc record created
  - [ ] Account.is_ekyc updated
  - [ ] Data securely stored

### 4.8 Device Session Management

#### FR-H01: Register Device

- **Description**: Register device for push notifications
- **Input**: account_id, device_token, device_info
- **Output**: Device session created
- **Acceptance Criteria**:
  - [ ] Device token stored
  - [ ] Platform identified (iOS/Android)

#### FR-H02: List User Devices

- **Description**: List all devices for a user
- **Input**: account_id
- **Output**: List of registered devices
- **Acceptance Criteria**:
  - [ ] Returns all active devices
  - [ ] Includes last activity time

#### FR-H03: Revoke Device

- **Description**: Remove device session
- **Input**: device_id or account_id
- **Output**: Device removed
- **Acceptance Criteria**:
  - [ ] Device can no longer receive notifications
  - [ ] Session invalidated

---

## 5. Non-Functional Requirements

### 5.1 Performance

#### NFR-P01: API Latency

- **Description**: 90% of API requests must respond within 200ms
- **Measurement**: P90 latency measured at service level
- **Acceptance Criteria**:
  - [ ] P90 latency < 200ms under normal load
  - [ ] P99 latency < 500ms under normal load

#### NFR-P02: Throughput

- **Description**: Service must handle 500 concurrent users
- **Measurement**: Load testing with concurrent connections
- **Acceptance Criteria**:
  - [ ] Stable performance at 500 concurrent users
  - [ ] Graceful degradation beyond capacity

#### NFR-P03: Token Validation

- **Description**: JWT validation must complete within 10ms
- **Measurement**: Token validation benchmark
- **Acceptance Criteria**:
  - [ ] Average validation < 10ms
  - [ ] Blacklist check optimized with Redis

### 5.2 Security

#### NFR-S01: Password Security

- **Description**: Passwords must be securely hashed
- **Implementation**: bcrypt with cost factor 10+
- **Acceptance Criteria**:
  - [ ] Passwords never stored in plain text
  - [ ] Hash verified on authentication

#### NFR-S02: Token Security

- **Description**: JWT tokens must be secure
- **Implementation**: 
  - Separate secrets for web and app
  - Access token: 1 hour expiry
  - Refresh token: 7 days expiry
- **Acceptance Criteria**:
  - [ ] Tokens signed with HS256
  - [ ] Secrets stored in Vault
  - [ ] Blacklist enforced

#### NFR-S03: API Authentication

- **Description**: All gRPC endpoints must be authenticated
- **Exceptions**: Login, Register, OTP endpoints
- **Acceptance Criteria**:
  - [ ] Unauthenticated requests rejected
  - [ ] Valid tokens accepted
  - [ ] API keys for service-to-service

#### NFR-S04: Data Encryption

- **Description**: Sensitive data must be encrypted at rest
- **Scope**: eKYC images, personal identifiers
- **Acceptance Criteria**:
  - [ ] Images encrypted before storage
  - [ ] Encryption keys managed securely

### 5.3 Reliability

#### NFR-R01: Availability

- **Description**: Service must have 99.9% uptime
- **Measurement**: Monthly uptime percentage
- **Acceptance Criteria**:
  - [ ] Max 43 minutes downtime per month
  - [ ] Health checks pass

#### NFR-R02: Database Connection

- **Description**: Database connections must be resilient
- **Implementation**: Connection pooling, retry logic
- **Acceptance Criteria**:
  - [ ] Automatic reconnection on failure
  - [ ] Connection pool managed

### 5.4 Maintainability

#### NFR-M01: Code Coverage

- **Description**: Unit test coverage minimum 80%
- **Measurement**: Go test coverage report
- **Acceptance Criteria**:
  - [ ] Coverage report shows >= 80%

#### NFR-M02: Logging

- **Description**: All operations must be logged
- **Implementation**: Structured logging with Zap
- **Acceptance Criteria**:
  - [ ] Request/response logged
  - [ ] Errors logged with context
  - [ ] No sensitive data in logs

---

## 6. Technical Constraints

### TC-001: Proto-First Design

- **Description**: All service contracts defined in Core repository
- **Impact**: Must update Core before service implementation
- **Acceptance Criteria**:
  - [ ] Proto files in Core
  - [ ] Service imports generated code

### TC-002: Database Schema

- **Description**: Must use existing PostgreSQL schema
- **Impact**: Schema changes require migrations
- **Acceptance Criteria**:
  - [ ] Migrations applied on startup
  - [ ] Backward compatible changes

### TC-003: Authentication Interoperability

- **Description**: Must support both web and mobile clients
- **Impact**: Separate JWT secrets per platform
- **Acceptance Criteria**:
  - [ ] Web tokens use secret_key_web
  - [ ] App tokens use secret_key_app

---

## 7. Explicit Non-Goals

The following are intentionally NOT addressed in this document:

- Mobile app UI/UX design
- Web portal implementation
- Notification delivery logic (handled by Notification Service)
- Payment processing
- Reporting and analytics dashboards
- Third-party API rate limiting configuration

---

## 8. Acceptance Criteria Summary

### Functional Criteria
- [ ] All authentication flows working (email, phone, SSO)
- [ ] CRUD operations for all entities
- [ ] RBAC enforcement on all protected endpoints
- [ ] eKYC integration functional

### Technical Criteria
- [ ] gRPC services exposed on port 50051
- [ ] Health check endpoints available
- [ ] Metrics exposed for monitoring
- [ ] Logs structured and queryable

### Performance Criteria
- [ ] P90 latency < 200ms
- [ ] 500 concurrent users supported
- [ ] Token validation < 10ms

### Security Criteria
- [ ] All passwords hashed
- [ ] Tokens properly signed and validated
- [ ] Sensitive data encrypted

---

## 9. Appendix

### A. Entity Relationship Summary

```
Account (1) ──── (1) User
Account (1) ──── (0..1) Farmer
Account (1) ──── (0..1) Supplier
Account (1) ──── (0..1) Ekyc
Account (1) ──── (0..n) DeviceSession
Account (n) ──── (n) Role (via Casbin)
Role (n) ──── (n) Permission
Farmer (1) ──── (0..n) ParcelLand
ParcelLand (1) ──── (0..n) PolygonCoordinate
```

### B. API Endpoint Mapping

| gRPC Service | Method | Description |
| --- | --- | --- |
| AuthService | Login | User authentication |
| AuthService | Register | New user registration |
| AuthService | RefreshToken | Token refresh |
| AuthService | RevokeToken | Logout |
| AccountService | CreateAccount | Create account |
| AccountService | GetAccount | Get account by ID |
| AccountService | ListAccounts | List with filters |
| AccountService | UpdateAccount | Update account |
| AccountService | DeleteAccount | Soft delete |
| UserService | GetUser | Get user profile |
| UserService | UpdateUser | Update profile |
| FarmerService | CreateFarmer | Create farmer |
| FarmerService | GetFarmer | Get farmer |
| FarmerService | ListFarmers | List farmers |
| FarmerService | UpdateFarmer | Update farmer |
| SupplierService | CreateSupplier | Create supplier |
| SupplierService | GetSupplier | Get supplier |
| SupplierService | ListSuppliers | List suppliers |
| SupplierService | UpdateSupplier | Update supplier |
