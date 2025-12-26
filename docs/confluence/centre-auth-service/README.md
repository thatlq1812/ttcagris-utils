# Centre Auth Service (CAS)

***Created:*** 2025-12-26

***Last Updated:*** 2025-12-26

***Version:*** 1.0.0

***Status:*** Active

---

## Overview

**Centre Auth Service (CAS)** is the centralized authentication and authorization microservice for the AgriOS Platform. It manages user identities, authentication flows, role-based access control (RBAC), and integrates with external services for eKYC verification.

**Key Responsibilities:**
- User authentication (email, phone, SSO)
- Account and identity management
- Role-based access control (RBAC)
- JWT token management
- eKYC identity verification
- Farmer and supplier profile management

---

## Quick Reference

| Item | Value |
| --- | --- |
| **gRPC Port** | 50051 |
| **HTTP Port** | 4000 |
| **Database** | PostgreSQL 17+ |
| **Cache** | Redis 7+ |
| **Language** | Go 1.25+ |

---

## Key Features

### Authentication
- Email/password authentication
- Phone/OTP authentication
- Azure SSO integration
- JWT access and refresh tokens
- Device session management

### User Management
- Account CRUD operations
- User profile management
- Farmer registration and management
- Supplier registration and management

### Authorization
- Role-based access control (RBAC) via Casbin
- Permission management
- API-level authorization

### eKYC Integration
- OCR for ID card reading
- Face liveness detection
- Face comparison
- Identity verification workflow

---

## Architecture

```
┌─────────────────┐      ┌─────────────────┐
│   API Gateway   │─────▶│       CAS       │
│   (REST/JSON)   │      │   (gRPC:50051)  │
└─────────────────┘      └────────┬────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
   │  PostgreSQL │         │    Redis    │         │   Azure     │
   │  (Database) │         │   (Cache)   │         │   Blob      │
   └─────────────┘         └─────────────┘         └─────────────┘
```

---

## Domain Entities

| Entity | Description |
| --- | --- |
| **Account** | Authentication identity (email/phone/SSO) |
| **User** | Personal profile linked to account |
| **Farmer** | Agricultural producer profile |
| **Supplier** | Service provider profile |
| **Ekyc** | Identity verification data |
| **Role** | Access control role |
| **Permission** | API endpoint access rights |

---

## gRPC Services

| Service | Description |
| --- | --- |
| `AuthService` | Login, logout, token management |
| `MobileAuthService` | Mobile-specific authentication |
| `AccountService` | Account CRUD operations |
| `UserService` | User profile management |
| `FarmerService` | Farmer management |
| `SupplierService` | Supplier management |
| `RoleService` | Role management |
| `PermissionService` | Permission management |
| `EkycService` | eKYC operations |
| `DeviceService` | Device session management |

---

## Related Documents

| Document | Description | Audience |
| --- | --- | --- |
| [SRS_centre_auth_service.md](SRS_centre_auth_service.md) | Software Requirements Specification | PO, QA, Dev |
| [TDD_centre_auth_service.md](TDD_centre_auth_service.md) | Technical Design Document | Dev, DevOps |
| [PROC_development_workflow.md](PROC_development_workflow.md) | Development Process | Dev |
| [centre-auth-service/README.md](../../../centre-auth-service/README.md) | Technical README | Dev |

---

## Contact

- **Team**: Backend Team
- **Repository**: `dev.azure.com/agris-agriculture/Core/_git/centre-auth-service`
