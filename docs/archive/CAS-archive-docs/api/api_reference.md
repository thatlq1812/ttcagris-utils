# Centre Auth Service - API Reference

**Author:** thatlq1812  
**Created:** 2025-12-18  
**Last Updated:** 2025-12-18  
**Version:** 1.0.0  
**Status:** Active

---

## Overview

This document provides the complete API reference for Centre Auth Service (CAS). All endpoints are exposed via gRPC (port 50051) and can be accessed through the API Gateway (port 8080) which translates REST/JSON to gRPC.

**Base URL (via Gateway):** `http://localhost:8080/api/v1`  
**Direct gRPC:** `localhost:50051`

---

## Authentication

Most endpoints require authentication via JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

**Token Types:**
- **Access Token:** Short-lived (15 minutes), used for API requests
- **Refresh Token:** Long-lived (7 days), used to obtain new access tokens

**Public Endpoints** (no authentication required):
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/azure-callback`
- `POST /mobile/send-register-otp`
- `POST /mobile/check-phone-exists`
- `GET /permissions/list`

---

## Service: AuthService

Package: `auth.v1`  
Proto: [proto/auth/v1/auth.proto](../../proto/auth/v1/auth.proto)

### Register

Create a new user account with email or phone identifier.

**Endpoint:** `POST /auth/register`  
**gRPC Method:** `auth.v1.AuthService/Register`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "name": "John Doe",
  "type": "email",           // Optional: "email" or "phone" (auto-detected if omitted)
  "identifier": "john@example.com",  // Email or phone number
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Registration successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "account": {
      "id": 1,
      "type": "email",
      "identifier": "john@example.com",
      "provider": "local",
      "created_at": "2025-12-18T10:00:00Z",
      "name": "John Doe",
      "is_ekyc": false,
      "is_farmer": false,
      "is_supplier": false
    }
  }
}
```

---

### Login

Authenticate with email/phone and password.

**Endpoint:** `POST /auth/login`  
**gRPC Method:** `auth.v1.AuthService/Login`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "identifier": "john@example.com",
  "password": "SecurePass123",
  "provider": "local",          // Optional: "local", "azure"
  "name": "John Doe",           // Optional: for first-time SSO users
  "device_info": {              // Optional: device tracking
    "device_id": "uuid-1234",
    "device_type": "mobile",
    "device_name": "iPhone 14",
    "os_version": "iOS 17.0",
    "app_version": "1.0.0",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "account": {
      "id": 1,
      "identifier": "john@example.com",
      "type": "email",
      "provider": "local",
      "created_at": "2025-12-18T10:00:00Z",
      "name": "John Doe",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "phone": "+84901234567",
      "email": "john@example.com",
      "ekyc": null,
      "farmer_id": 0,
      "supplier_id": 0,
      "is_ekyc": false,
      "is_farmer": false,
      "is_supplier": false,
      "is_active_farmer": false,
      "is_active_supplier": false
    }
  }
}
```

---

### Refresh Token

Obtain a new access token using a refresh token.

**Endpoint:** `POST /auth/refresh`  
**gRPC Method:** `auth.v1.AuthService/RefreshToken`  
**Authentication:** None (uses refresh token)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

### Logout

Invalidate refresh token and access token.

**Endpoint:** `POST /auth/logout`  
**gRPC Method:** `auth.v1.AuthService/Logout`  
**Authentication:** Required

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Logout successful",
  "data": {
    "message": "User logged out successfully"
  }
}
```

---

### Get Profile

Get authenticated user's profile.

**Endpoint:** `GET /auth/profile`  
**gRPC Method:** `auth.v1.AuthService/GetProfile`  
**Authentication:** Required

**Response:**
```json
{
  "code": "200",
  "message": "Profile retrieved successfully",
  "data": {
    "account": {
      "id": 1,
      "identifier": "john@example.com",
      "type": "email",
      "name": "John Doe",
      "phone": "+84901234567",
      "email": "john@example.com",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "address": "123 Main St",
      "is_ekyc": true,
      "is_farmer": true,
      "farmer_id": 5,
      "ekyc": {
        "id_number": "001234567890",
        "full_name": "JOHN DOE",
        "date_of_birth": "15/01/1990",
        "issue_date": "01/01/2020",
        "expiry_date": "01/01/2030"
      }
    }
  }
}
```

---

### Verify Token

Validate an access token.

**Endpoint:** `POST /auth/verify-token`  
**gRPC Method:** `auth.v1.AuthService/VerifyToken`  
**Authentication:** Required

**Request Body:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Token is valid",
  "data": {
    "account_id": 1,
    "identifier": "john@example.com",
    "is_valid": true
  }
}
```

---

### Change Password

Change authenticated user's password.

**Endpoint:** `POST /auth/change-password`  
**gRPC Method:** `auth.v1.AuthService/ChangePassword`  
**Authentication:** Required

**Request Body:**
```json
{
  "old_password": "OldPass123",
  "new_password": "NewSecurePass456"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Password changed successfully"
}
```

---

### Azure AD Callback

Handle Azure AD SSO callback.

**Endpoint:** `POST /auth/azure-callback`  
**gRPC Method:** `auth.v1.AuthService/AzureCallback`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "code": "authorization_code_from_azure",
  "state": "csrf_token"
}
```

---

## Service: MobileAuthService

Package: `mobile.v1`  
Proto: [proto/mobile/v1/mobile_auth.proto](../../proto/mobile/v1/mobile_auth.proto)

### Send Register OTP

Send OTP code to phone number for registration.

**Endpoint:** `POST /mobile/send-register-otp`  
**gRPC Method:** `mobile.v1.MobileAuthService/SendRegisterOTP`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "phone_number": "+84901234567"  // E.164 format required
}
```

**Response:**
```json
{
  "code": "200",
  "message": "OTP sent successfully",
  "data": {
    "code": "otp-uuid-1234",
    "message": "OTP sent successfully to Telegram",
    "expires_at": "2025-12-18T10:02:00+07:00"
  }
}
```

**Rate Limiting:**
- Max 5 OTP per phone number per day
- 120 seconds cooldown between requests
- OTP expires in 120 seconds

---

### Verify OTP

Verify OTP code (before registration).

**Endpoint:** `POST /mobile/verify-otp`  
**gRPC Method:** `mobile.v1.MobileAuthService/VerifyOTP`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "phone_number": "+84901234567",
  "otp_id": "otp-uuid-1234",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "OTP verified successfully",
  "data": {
    "verified": true,
    "grace_period_seconds": 180  // Time window to complete registration
  }
}
```

---

### Register (Mobile)

Register new mobile account after OTP verification.

**Endpoint:** `POST /mobile/register`  
**gRPC Method:** `mobile.v1.MobileAuthService/Register`  
**Authentication:** None (requires verified OTP)

**Request Body:**
```json
{
  "phone_number": "+84901234567",
  "otp_id": "otp-uuid-1234",
  "pin": "123456",              // 6-digit PIN
  "name": "John Doe",
  "date_of_birth": "1990-01-15", // Optional: YYYY-MM-DD
  "gender": "male",              // Optional: "male", "female", "other"
  "device_info": {
    "device_id": "uuid-1234",
    "device_type": "mobile",
    "device_name": "iPhone 14",
    "os_version": "iOS 17.0",
    "app_version": "1.0.0"
  }
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Registration successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "account": {
      "id": 1,
      "identifier": "+84901234567",
      "code": "ABC12345",        // 8-character unique immutable code
      "created_at": "2025-12-18T10:00:00Z",
      "name": "John Doe",
      "phone": "+84901234567",
      "is_ekyc": false
    }
  }
}
```

---

### Login with PIN

Authenticate mobile user with phone and PIN.

**Endpoint:** `POST /mobile/login`  
**gRPC Method:** `mobile.v1.MobileAuthService/LoginWithPIN`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "phone_number": "+84901234567",
  "pin": "123456",
  "device_info": {
    "device_id": "uuid-1234",
    "device_type": "mobile"
  }
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "account": {
      "id": 1,
      "identifier": "+84901234567",
      "code": "ABC12345",
      "name": "John Doe",
      "phone": "+84901234567",
      "is_ekyc": true,
      "is_farmer": true,
      "farmer_id": 5,
      "ekyc": {
        "id_number": "001234567890",
        "full_name": "JOHN DOE"
      }
    }
  }
}
```

---

### Send Reset PIN OTP

Send OTP for PIN reset.

**Endpoint:** `POST /mobile/send-reset-pin-otp`  
**gRPC Method:** `mobile.v1.MobileAuthService/SendResetPINOTP`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "phone_number": "+84901234567"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "OTP sent successfully",
  "data": {
    "code": "200",
    "id": "otp-uuid-5678",
    "phone_number": "+84901234567",
    "expires_at": "2025-12-18T10:02:00+07:00"
  }
}
```

---

### Reset PIN

Reset PIN using OTP.

**Endpoint:** `POST /mobile/reset-pin`  
**gRPC Method:** `mobile.v1.MobileAuthService/ResetPIN`  
**Authentication:** None (requires verified OTP)

**Request Body:**
```json
{
  "phone_number": "+84901234567",
  "otp_id": "otp-uuid-5678",
  "new_pin": "654321"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "PIN reset successfully",
  "data": {
    "code": "200",
    "message": "PIN has been reset"
  }
}
```

---

### Change PIN

Change PIN (requires authentication).

**Endpoint:** `POST /mobile/change-pin`  
**gRPC Method:** `mobile.v1.MobileAuthService/ChangePIN`  
**Authentication:** Required

**Request Body:**
```json
{
  "old_pin": "123456",
  "new_pin": "654321"
}
```

**Response:**
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

### Check Phone Exists

Check if phone number is already registered.

**Endpoint:** `POST /mobile/check-phone-exists`  
**gRPC Method:** `mobile.v1.MobileAuthService/CheckPhoneExists`  
**Authentication:** None (public)

**Request Body:**
```json
{
  "phone_number": "+84901234567"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Phone check completed",
  "data": {
    "exists": true
  }
}
```

---

## Service: AccountService

Package: `account.v1`  
Proto: [proto/account/v1/account.proto](../../proto/account/v1/account.proto)

### Get My Account

Get authenticated user's account details.

**Endpoint:** `GET /accounts/me`  
**gRPC Method:** `account.v1.AccountService/GetMyAccount`  
**Authentication:** Required

**Response:**
```json
{
  "code": "200",
  "message": "Account retrieved successfully",
  "data": {
    "account": {
      "id": 1,
      "code": "ABC12345",
      "identifier": "+84901234567",
      "source": "app",
      "type": "phone",
      "name": "John Doe",
      "phone": "+84901234567",
      "email": "john@example.com",
      "date_of_birth": "1990-01-15",
      "gender": "male",
      "address": "123 Main St",
      "is_ekyc": true,
      "is_farmer": true,
      "is_supplier": false,
      "is_frm_farmer": false,
      "farmer_id": 5,
      "supplier_id": 0,
      "created_at": "2025-12-18T10:00:00Z"
    }
  }
}
```

---

### Update My Account

Update authenticated user's account.

**Endpoint:** `PUT /accounts/me`  
**gRPC Method:** `account.v1.AccountService/UpdateMyAccount`  
**Authentication:** Required

**Request Body:**
```json
{
  "identifier": "+84901234567",
  "name": "John Updated Doe",
  "phone": "+84901234567",
  "email": "john.updated@example.com",
  "address": "456 New St",
  "date_of_birth": "1990-01-15",
  "gender": "male"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Account updated successfully",
  "data": {
    "account": {
      "id": 1,
      "name": "John Updated Doe",
      "email": "john.updated@example.com"
    }
  }
}
```

---

### List Accounts

List all accounts with filters and pagination (admin only).

**Endpoint:** `GET /accounts`  
**gRPC Method:** `account.v1.AccountService/ListAccounts`  
**Authentication:** Required (admin)

**Query Parameters:**
```
page=1
size=20
search=john                    // Search in name and email
filters[0][field]=source
filters[0][operator]=$eq
filters[0][values][0]=app
filters[1][field]=is_farmer
filters[1][operator]=$eq
filters[1][values][0]=true
sort[0][field]=created_at
sort[0][order]=desc
```

**Supported Filter Operators:**
- `$eq`: Equal
- `$ne`: Not equal
- `$gt`: Greater than
- `$gte`: Greater than or equal
- `$lt`: Less than
- `$lte`: Less than or equal
- `$in`: In array
- `$nin`: Not in array
- `$contains`: Contains substring
- `$null`: Is null (values can be ["true"] or ["false"])

**Response:**
```json
{
  "code": "200",
  "message": "Accounts retrieved successfully",
  "data": {
    "accounts": [
      {
        "id": 1,
        "code": "ABC12345",
        "identifier": "+84901234567",
        "name": "John Doe",
        "is_farmer": true
      }
    ],
    "total": 150,
    "page": 1,
    "size": 20,
    "has_more": true
  }
}
```

---

### Get My Parcel Lands

Get authenticated farmer's land parcels.

**Endpoint:** `GET /accounts/me/parcel-lands`  
**gRPC Method:** `account.v1.AccountService/GetMyParcelLands`  
**Authentication:** Required

**Response:**
```json
{
  "code": "200",
  "message": "Parcel lands retrieved successfully",
  "data": {
    "parcel_lands": [
      {
        "id": 1,
        "name": "Rice Field A",
        "area": 5000.5,
        "farmer_id": 5,
        "coordinates": [
          {
            "id": 1,
            "latitude": 10.8231,
            "longitude": 106.6297,
            "order": 1
          },
          {
            "id": 2,
            "latitude": 10.8235,
            "longitude": 106.6305,
            "order": 2
          }
        ]
      }
    ]
  }
}
```

---

## Service: RoleService

Package: `role.v1`  
Proto: [proto/role/v1/role.proto](../../proto/role/v1/role.proto)

### Create Role

Create a new role with permissions.

**Endpoint:** `POST /roles`  
**gRPC Method:** `role.v1.RoleService/CreateRole`  
**Authentication:** Required (admin)

**Request Body:**
```json
{
  "name": "Farmer Manager",
  "description": "Manages farmer accounts and data",
  "permission_ids": [1, 2, 3, 5, 8]
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Role created successfully",
  "data": {
    "role": {
      "id": 10,
      "code": "1734516000123456789",  // Unix nanosecond timestamp
      "name": "Farmer Manager",
      "description": "Manages farmer accounts and data"
    }
  }
}
```

---

### Get Role

Get role details by code.

**Endpoint:** `GET /roles/{role_code}`  
**gRPC Method:** `role.v1.RoleService/GetRole`  
**Authentication:** Required

**Response:**
```json
{
  "code": "200",
  "message": "Role retrieved successfully",
  "data": {
    "role": {
      "id": 10,
      "code": "1734516000123456789",
      "name": "Farmer Manager",
      "description": "Manages farmer accounts and data"
    }
  }
}
```

---

### List Roles

List all roles with pagination.

**Endpoint:** `GET /roles`  
**gRPC Method:** `role.v1.RoleService/ListRoles`  
**Authentication:** Required

**Query Parameters:**
```
page=1
size=20
```

**Response:**
```json
{
  "code": "200",
  "message": "Roles retrieved successfully",
  "data": {
    "roles": [
      {
        "code": "admin",
        "name": "Administrator",
        "description": "Full system access",
        "account_count": 5,
        "permission_count": 150
      },
      {
        "code": "farmer_manager",
        "name": "Farmer Manager",
        "description": "Manages farmers",
        "account_count": 12,
        "permission_count": 25
      }
    ],
    "total": 15,
    "page": 1,
    "size": 20
  }
}
```

---

### Assign Role to Account

Assign a role to an account.

**Endpoint:** `POST /roles/assign`  
**gRPC Method:** `role.v1.RoleService/AssignRoleToAccount`  
**Authentication:** Required (admin)

**Request Body:**
```json
{
  "account_id": 123,
  "role_code": "farmer_manager",
  "domain": "HUB001"  // Hub code or "*" for all domains
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Role assigned successfully"
}
```

---

### Get Account Roles

Get all roles assigned to an account.

**Endpoint:** `GET /accounts/{account_id}/roles`  
**gRPC Method:** `role.v1.RoleService/GetAccountRoles`  
**Authentication:** Required

**Response:**
```json
{
  "code": "200",
  "message": "Account roles retrieved successfully",
  "data": {
    "roles": [
      {
        "account_id": 123,
        "role": "farmer_manager",
        "domain": "HUB001"
      },
      {
        "account_id": 123,
        "role": "viewer",
        "domain": "*"
      }
    ]
  }
}
```

---

### Check Permission

Check if account has permission for resource/action.

**Endpoint:** `POST /roles/check-permission`  
**gRPC Method:** `role.v1.RoleService/CheckPermission`  
**Authentication:** Required

**Request Body:**
```json
{
  "account_id": 123,
  "resource": "/api/v1/farmers",
  "action": "write",
  "domain": "HUB001"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Permission check completed",
  "data": {
    "allowed": true
  }
}
```

---

## Service: PermissionService

Package: `permission.v1`  
Proto: [proto/permission/v1/permission.proto](../../proto/permission/v1/permission.proto)

### List Permissions

List all permissions (gRPC endpoints) grouped by service.

**Endpoint:** `GET /permissions`  
**gRPC Method:** `permission.v1.PermissionService/ListPermissions`  
**Authentication:** None (public)

**Query Parameters:**
```
service_name=auth.v1.AuthService  // Optional filter
search=login                       // Optional search
page=1
size=50
```

**Response:**
```json
{
  "code": "200",
  "message": "Permissions retrieved successfully",
  "data": {
    "groups": [
      {
        "service_name": "auth.v1.AuthService",
        "count": 10,
        "permissions": [
          {
            "id": 1,
            "endpoint": "/auth.v1.AuthService/Login",
            "service_name": "auth.v1.AuthService",
            "method_name": "Login",
            "description": "User login endpoint"
          },
          {
            "id": 2,
            "endpoint": "/auth.v1.AuthService/Register",
            "service_name": "auth.v1.AuthService",
            "method_name": "Register",
            "description": "User registration endpoint"
          }
        ]
      },
      {
        "service_name": "farmer.v1.FarmerService",
        "count": 7,
        "permissions": [...]
      }
    ],
    "total": 150,
    "page": 1,
    "size": 50,
    "has_more": true
  }
}
```

---

### Get Role Permissions

Get all permissions assigned to a role.

**Endpoint:** `GET /permissions/role/{role_code}`  
**gRPC Method:** `permission.v1.PermissionService/GetRolePermissions`  
**Authentication:** Required

**Response:**
```json
{
  "code": "200",
  "message": "Role permissions retrieved successfully",
  "data": {
    "role_code": "farmer_manager",
    "permissions": [
      {
        "id": 15,
        "endpoint": "/farmer.v1.FarmerService/CreateFarmer",
        "service_name": "farmer.v1.FarmerService",
        "method_name": "CreateFarmer"
      }
    ]
  }
}
```

---

## Service: FarmerService

Package: `farmer.v1`  
Proto: [proto/farmer/v1/farmer.proto](../../proto/farmer/v1/farmer.proto)

### Create Farmer

Create farmer profile for authenticated account.

**Endpoint:** `POST /farmers`  
**gRPC Method:** `farmer.v1.FarmerService/CreateFarmer`  
**Authentication:** Required

**Request Body:**
```json
{
  "agricultural_officer": "Officer Name",
  "area": 5000.5,
  "avarta_url": "https://example.com/avatar.jpg",
  "crop_types": ["rice", "corn"],
  "cultivated_area": {
    "rice": 3000,
    "corn": 2000
  },
  "customer_code": "FARM001",
  "customer_group": "Group A",
  "customer_type": "Premium",
  "img_front_url": "https://example.com/id-front.jpg",
  "img_back_url": "https://example.com/id-back.jpg",
  "investment_area": "Zone A",
  "investment_programs": ["Program 1", "Program 2"],
  "investment_zone": "North",
  "status": "active",
  "is_skip": false,
  "is_contact": true
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Farmer created successfully",
  "data": {
    "farmer": {
      "id": 5,
      "account_id": 1,
      "customer_code": "FARM001",
      "area": 5000.5,
      "status": "active"
    }
  }
}
```

---

### Get My Farmer

Get authenticated account's farmer profile.

**Endpoint:** `GET /farmers/me`  
**gRPC Method:** `farmer.v1.FarmerService/GetMyFarmer`  
**Authentication:** Required

**Response:**
```json
{
  "code": "200",
  "message": "Farmer retrieved successfully",
  "data": {
    "farmer": {
      "id": 5,
      "account_id": 1,
      "customer_code": "FARM001",
      "area": 5000.5,
      "crop_types": ["rice", "corn"],
      "status": "active"
    }
  }
}
```

---

### Update Farmer

Update authenticated account's farmer profile.

**Endpoint:** `PUT /farmers/me`  
**gRPC Method:** `farmer.v1.FarmerService/UpdateFarmer`  
**Authentication:** Required

**Request Body:** (same as CreateFarmer)

---

## Service: SupplierService

Package: `supplier.v1`  
Proto: [proto/supplier/v1/supplier.proto](../../proto/supplier/v1/supplier.proto)

### Create Supplier

Create supplier profile for authenticated account.

**Endpoint:** `POST /suppliers`  
**gRPC Method:** `supplier.v1.SupplierService/CreateSupplier`  
**Authentication:** Required

**Request Body:**
```json
{
  "business_name": "ABC Supplies Ltd",
  "business_fields": ["fertilizer", "seeds"],
  "representative_position": "Sales Manager",
  "tax_code": "0123456789",
  "business_license": "BL-2023-001",
  "status": "active"
}
```

**Response:**
```json
{
  "code": "200",
  "message": "Supplier created successfully",
  "data": {
    "supplier": {
      "id": 10,
      "account_id": 1,
      "business_name": "ABC Supplies Ltd",
      "tax_code": "0123456789",
      "status": "active"
    }
  }
}
```

---

## Service: DeviceService

Package: `device.v1`  
Proto: [proto/device/v1/device.proto](../../proto/device/v1/device.proto)

### Get Devices by Account ID

Get all device sessions for an account.

**Endpoint:** `GET /devices/account/{account_id}`  
**gRPC Method:** `device.v1.DeviceService/GetDevicesByAccountID`  
**Authentication:** Required (admin or own account)

**Response:**
```json
{
  "code": "200",
  "message": "Devices retrieved successfully",
  "data": {
    "devices": [
      {
        "id": 1,
        "account_id": 123,
        "device_id": "uuid-1234",
        "device_type": "mobile",
        "device_name": "iPhone 14",
        "os_version": "iOS 17.0",
        "app_version": "1.0.0",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0...",
        "last_active_at": "2025-12-18T10:00:00Z",
        "is_active": true,
        "created_at": "2025-12-01T10:00:00Z"
      }
    ]
  }
}
```

---

## Service: eKYC Services

Package: `ekyc.v1`  
Proto: [proto/ekyc/v1/*.proto](../../proto/ekyc/v1/)

CAS provides 10 eKYC service proxies to the external eKYC provider:

1. **FileService** - Upload documents
2. **OCRService** - Extract OCR data from ID cards
3. **LivenessService** - Card liveness detection
4. **FaceLivenessService** - Face liveness (2D)
5. **FaceLiveness3DService** - Face liveness (3D)
6. **FaceCompareService** - 1:1 face comparison
7. **FaceCompareGeneralService** - 1:N face comparison
8. **FaceMaskService** - Face mask detection
9. **EKYCAuthService** - eKYC authentication
10. **EkycDataService** - eKYC data management

These services forward requests to the external eKYC provider configured in `config.yaml`. Refer to the eKYC provider's documentation for detailed API specifications.

---

## Error Responses

All errors follow a consistent format:

```json
{
  "code": "400",
  "message": "Invalid request",
  "error": {
    "status": 400,
    "code": "ERR-01",
    "message": "Validation failed: email is required"
  }
}
```

### Common Error Codes

| HTTP Status | Code | Message |
|-------------|------|---------|
| 400 | ERR-01 | Invalid request parameters |
| 401 | ERR-02 | Unauthorized - invalid or expired token |
| 403 | ERR-03 | Forbidden - insufficient permissions |
| 404 | ERR-04 | Resource not found |
| 409 | ERR-05 | Conflict - resource already exists |
| 429 | ERR-06 | Rate limit exceeded |
| 500 | ERR-99 | Internal server error |

---

## Rate Limiting

OTP endpoints have rate limiting:

**SendRegisterOTP / SendResetPINOTP:**
- Max 5 requests per phone number per day
- 120 seconds cooldown between requests

**Headers:**
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1734518400
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
```
page=1    // Page number (1-indexed)
size=20   // Items per page (default: 20, max: 100)
```

**Response:**
```json
{
  "data": {
    "items": [...],
    "total": 150,
    "page": 1,
    "size": 20,
    "has_more": true
  }
}
```

---

## Testing with gRPCurl

Test gRPC endpoints directly:

```bash
# List services
grpcurl -plaintext localhost:50051 list

# List methods for AuthService
grpcurl -plaintext localhost:50051 list auth.v1.AuthService

# Call Login
grpcurl -plaintext -d '{
  "identifier": "john@example.com",
  "password": "SecurePass123"
}' localhost:50051 auth.v1.AuthService/Login

# Call with authentication
grpcurl -plaintext \
  -H "Authorization: Bearer YOUR_TOKEN" \
  localhost:50051 auth.v1.AuthService/GetProfile
```

---

## Testing via API Gateway

Test REST endpoints through gateway:

```bash
# Register
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "identifier": "john@example.com",
    "password": "SecurePass123"
  }'

# Login
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "john@example.com",
    "password": "SecurePass123"
  }'

# Get profile (with token)
curl http://localhost:8080/api/v1/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Navigation

### Documentation Home
- [Back to README](../../README.md) - Main documentation hub

### Related Documentation
- [Architecture Overview](../architecture/overview.md) - System design and components
- [Database Schema](../database/schema.md) - Data models and relationships  
- [Testing Guide](../guides/testing_guide.md) - How to test APIs
- [Deployment Guide](../guides/deployment_guide.md) - Production deployment

### Project Documentation
- [CHANGELOG](../../CHANGELOG.md) - Version history and updates
- [Port Allocation](../../../docs/PORT_ALLOCATION.md) - System-wide port assignments

**Version**: 1.0.0 | [Back to Top](#centre-auth-service-api-reference)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-18 | Initial API reference from proto files |
