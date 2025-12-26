# Centre Auth Service - Database Schema

**Author:** thatlq1812  
**Created:** 2025-12-18  
**Last Updated:** 2025-12-18  
**Version:** 1.0.0  
**Status:** Active

---

## Overview

This document describes the complete database schema for Centre Auth Service. The database uses PostgreSQL 14+ with 50+ tables and 70+ migrations tracking schema evolution.

**Database Name:** `centre_auth`  
**Schema:** `public`  
**Total Tables:** 50+  
**Total Migrations:** 70+

---

## Entity Relationship Diagram

### Core Authentication Flow

```mermaid
erDiagram
    users ||--o{ accounts : "has many"
    accounts ||--o{ refresh_tokens : "has many"
    accounts ||--o{ device_sessions : "has many"
    accounts ||--o| farmers : "has one"
    accounts ||--o| suppliers : "has one"
    accounts ||--o| ekycs : "has one"
    accounts ||--o| frm_farmers : "has one"
    accounts ||--o{ farmer_hubs : "has many"
    accounts ||--o{ supplier_hubs : "has many"
    accounts ||--o{ consent_logs : "has many"
    accounts }o--o{ roles : "has many through casbin_rule"
    
    farmers ||--o{ parcel_lands : "has many"
    parcel_lands ||--o{ polygon_coordinates : "has many"
    
    suppliers }o--o{ business_fields : "has many"
    suppliers }o--o{ representative_positions : "has many"
    
    consent_policies ||--o{ consent_logs : "has many"
    
    roles ||--o{ casbin_rule : "has many"
    permissions ||--o{ role_permissions : "has many"
    roles ||--o{ role_permissions : "has many"
    
    users {
        bigserial id PK
        varchar name
        date date_of_birth
        varchar gender
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }
    
    accounts {
        bigserial id PK
        bigint user_id FK
        varchar code UK
        varchar type
        varchar identifier UK
        varchar password_hash
        varchar provider
        varchar source
        boolean is_ekyc
        boolean is_farmer
        boolean is_supplier
        boolean is_frm_farmer
        boolean is_form
        boolean is_active_farmer
        boolean is_active_supplier
        boolean is_deactive
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }
    
    farmers {
        bigserial id PK
        bigint account_id FK UK
        varchar customer_code
        numeric area
        varchar status
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }
    
    suppliers {
        bigserial id PK
        bigint account_id FK UK
        varchar company_name
        varchar tax_code
        varchar status
        boolean is_deleted
        timestamp created_at
        timestamp updated_at
    }
```

---

## Core Tables

### users

Base user information table. Contains personal details shared across all account types.

**Purpose:** Store user personal information  
**Relationships:** One user can have multiple accounts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | User ID |
| name | VARCHAR(100) | NULLABLE | User display name |
| date_of_birth | DATE | | Birth date (YYYY-MM-DD) |
| gender | VARCHAR(20) | | Gender: male, female, other |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_users_name` on name
- `idx_users_created_at` on created_at DESC

**Example:**
```sql
INSERT INTO users (name, date_of_birth, gender) 
VALUES ('John Doe', '1990-01-15', 'male');
```

---

### accounts

Authentication accounts table. Each account represents one login method (email, phone, SSO).

**Purpose:** Store authentication credentials and account metadata  
**Relationships:** 
- Belongs to one user
- Has many refresh_tokens
- Has many device_sessions
- Has one farmer profile
- Has one supplier profile

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Account ID |
| user_id | BIGINT | NULLABLE, FK(users.id) | Reference to user |
| code | VARCHAR(8) | UNIQUE, NOT NULL | Unique 8-char account code (immutable) |
| type | VARCHAR(50) | NOT NULL | Account type: email, phone, sso |
| identifier | VARCHAR(255) | NOT NULL | Email, phone, or provider user ID |
| password_hash | TEXT | | Bcrypt password hash |
| provider | VARCHAR(50) | | SSO provider: azure, google |
| source | VARCHAR(50) | DEFAULT 'web' | Source: web, app |
| is_ekyc | BOOLEAN | DEFAULT FALSE | Has completed eKYC |
| is_farmer | BOOLEAN | DEFAULT FALSE | Has farmer profile |
| is_supplier | BOOLEAN | DEFAULT FALSE | Has supplier profile |
| is_frm_farmer | BOOLEAN | DEFAULT FALSE | Has FRM farmer record |
| is_form | BOOLEAN | DEFAULT FALSE | Has form data |
| is_active_farmer | BOOLEAN | DEFAULT FALSE | Active farmer status |
| is_active_supplier | BOOLEAN | DEFAULT FALSE | Active supplier status |
| is_deactive | BOOLEAN | DEFAULT FALSE | Account deactivated |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Unique Constraints:**
- `UNIQUE(type, identifier)` - One identifier per type
- `UNIQUE(code)` - Globally unique account code

**Indexes:**
- `idx_accounts_user_id` on user_id
- `idx_accounts_type` on type
- `idx_accounts_identifier` on identifier
- `idx_accounts_code` on code
- `idx_accounts_source` on source
- `idx_accounts_is_ekyc` on is_ekyc
- `idx_accounts_is_farmer` on is_farmer
- `idx_accounts_is_supplier` on is_supplier

**Example:**
```sql
INSERT INTO accounts (user_id, code, type, identifier, password_hash, source) 
VALUES (1, 'ABC12345', 'email', 'john@example.com', '$2a$10$...', 'web');
```

---

### refresh_tokens

JWT refresh tokens for maintaining user sessions.

**Purpose:** Store refresh tokens for token rotation  
**Relationships:** Belongs to one account

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Token ID |
| account_id | BIGINT | NOT NULL, FK(accounts.id) | Reference to account |
| token | TEXT | NOT NULL, UNIQUE | Refresh token value |
| expires_at | TIMESTAMP | NOT NULL | Expiration timestamp |
| is_revoked | BOOLEAN | NOT NULL, DEFAULT FALSE | Revocation status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_refresh_tokens_account_id` on account_id
- `idx_refresh_tokens_active` on (account_id, is_revoked, expires_at) WHERE is_revoked = FALSE

**Example:**
```sql
INSERT INTO refresh_tokens (account_id, token, expires_at) 
VALUES (1, 'eyJhbGci...', NOW() + INTERVAL '7 days');
```

---

### otp_verifications

One-Time Password (OTP) codes for mobile authentication.

**Purpose:** Store OTP codes for phone verification  
**Relationships:** None (standalone verification)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | OTP record ID |
| phone | VARCHAR(20) | NOT NULL | Phone number (E.164 format) |
| code | VARCHAR(6) | NOT NULL | 6-digit OTP code |
| expires_at | TIMESTAMP | NOT NULL | Expiration timestamp (120s) |
| verified | BOOLEAN | DEFAULT FALSE | Verification status |
| verified_at | TIMESTAMP | | Verification timestamp |
| attempts | INT | DEFAULT 0 | Verification attempts |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes:**
- `idx_otp_verifications_phone` on phone
- `idx_otp_verifications_code` on code

**Rate Limiting:**
- Max 5 OTP per phone per day
- 120 seconds cooldown between requests
- 180 seconds grace period after verification

**Example:**
```sql
INSERT INTO otp_verifications (id, phone, code, expires_at) 
VALUES (uuid_generate_v4(), '+84901234567', '123456', NOW() + INTERVAL '120 seconds');
```

---

### device_sessions

Device tracking for multi-device login support.

**Purpose:** Track user sessions across multiple devices  
**Relationships:** Belongs to one account

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Session ID |
| account_id | BIGINT | NOT NULL, FK(accounts.id) | Reference to account |
| firebase_token | TEXT | | Firebase Cloud Messaging token |
| device_id | VARCHAR(255) | NOT NULL | Device unique identifier |
| device_type | VARCHAR(50) | | Device type: mobile, tablet, web |
| device_name | VARCHAR(100) | | Device name: iPhone 14, etc. |
| os_version | VARCHAR(50) | | Operating system version |
| app_version | VARCHAR(50) | | Application version |
| ip_address | VARCHAR(45) | | IP address (IPv4/IPv6) |
| user_agent | TEXT | | Browser/app user agent |
| last_active_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last activity timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Active session status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_device_sessions_account_id` on account_id
- `idx_device_sessions_device_id` on device_id
- `idx_device_sessions_is_active` on is_active

---

## Domain Tables

### farmers

Farmer profile data for agricultural users.

**Purpose:** Store farmer-specific profile information  
**Relationships:** 
- Belongs to one account (one-to-one)
- Has many parcel_lands
- Has many farmer_hubs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Farmer ID |
| account_id | BIGINT | NOT NULL, UNIQUE, FK(accounts.id) | Reference to account |
| agricultural_officer | VARCHAR(255) | | Assigned agricultural officer |
| area | NUMERIC(10,2) | | Total farm area (m²) |
| avarta_url | TEXT | | Profile avatar URL |
| crop_types | TEXT[] | | Array of crop types |
| cultivated_area | JSONB | | Cultivated area by crop (JSON) |
| customer_code | VARCHAR(50) | | Customer code from CRM |
| customer_group | VARCHAR(100) | | Customer group category |
| customer_type | VARCHAR(100) | | Customer type classification |
| img_front_url | TEXT | | ID card front image URL |
| img_back_url | TEXT | | ID card back image URL |
| investment_area | VARCHAR(255) | | Investment area/region |
| investment_programs | TEXT[] | | Array of investment programs |
| investment_zone | VARCHAR(255) | | Investment zone |
| status | VARCHAR(50) | | Status: active, inactive, pending |
| is_skip | BOOLEAN | DEFAULT FALSE | Skip certain validations |
| is_contact | BOOLEAN | DEFAULT FALSE | Contact preference flag |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_farmers_account_id` on account_id UNIQUE
- `idx_farmers_customer_code` on customer_code
- `idx_farmers_status` on status

**Example:**
```sql
INSERT INTO farmers (account_id, area, customer_code, status) 
VALUES (1, 5000.50, 'FARM001', 'active');
```

---

### parcel_lands

Land parcel information for farmers with GIS data.

**Purpose:** Store individual land parcel details  
**Relationships:** 
- Belongs to one farmer
- Has many polygon_coordinates (GIS boundary)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Parcel ID |
| farmer_id | BIGINT | FK(farmers.id) | Reference to farmer |
| parcel_id | VARCHAR(255) | | External parcel identifier |
| parcel_code | VARCHAR(100) | | Parcel code |
| parcel_number | VARCHAR(100) | | Parcel number |
| owner | VARCHAR(255) | | Land owner name |
| customer_code | VARCHAR(50) | | Customer code |
| area | NUMERIC(10,2) | | Parcel area (m²) |
| station | VARCHAR(255) | | Station/location |
| agricultural_officer | VARCHAR(255) | | Assigned officer |
| crop_type | VARCHAR(100) | | Current crop type |
| plant_type | VARCHAR(100) | | Plant type |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_parcel_lands_farmer_id` on farmer_id
- `idx_parcel_lands_parcel_code` on parcel_code
- `idx_parcel_lands_customer_code` on customer_code

---

### polygon_coordinates

GIS polygon coordinates for land parcel boundaries.

**Purpose:** Store GPS coordinates defining parcel boundaries  
**Relationships:** Belongs to one parcel_land

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Coordinate ID |
| parcel_land_id | BIGINT | NOT NULL, FK(parcel_lands.id) | Reference to parcel |
| latitude | NUMERIC(10,8) | NOT NULL | GPS latitude |
| longitude | NUMERIC(11,8) | NOT NULL | GPS longitude |
| order | INT | NOT NULL | Point order in polygon |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_polygon_coordinates_parcel_land_id` on parcel_land_id

**Example:**
```sql
INSERT INTO polygon_coordinates (parcel_land_id, latitude, longitude, "order") 
VALUES (1, 10.823100, 106.629700, 1);
```

---

### suppliers

Supplier profile data for input/service providers.

**Purpose:** Store supplier company information  
**Relationships:** 
- Belongs to one account (one-to-one)
- Has many supplier_hubs
- Has many-to-many business_fields
- Has many-to-many representative_positions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Supplier ID |
| account_id | BIGINT | NOT NULL, UNIQUE, FK(accounts.id) | Reference to account |
| company_name | VARCHAR(255) | | Company name |
| business_license | VARCHAR(100) | | Business license number |
| tax_code | VARCHAR(50) | | Tax identification number |
| company_address | TEXT | | Company address |
| contact_person | VARCHAR(255) | | Contact person name |
| contact_phone | VARCHAR(20) | | Contact phone |
| contact_email | VARCHAR(255) | | Contact email |
| business_field_ids | BIGINT[] | | Array of business field IDs |
| representative_position_ids | BIGINT[] | | Array of representative position IDs |
| service_areas | TEXT[] | | Array of service areas |
| status | VARCHAR(50) | | Status: active, pending, rejected |
| rating | NUMERIC(3,2) | | Average rating (0.00-5.00) |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_suppliers_account_id` on account_id UNIQUE
- `idx_suppliers_status` on status
- `idx_suppliers_tax_code` on tax_code

---

### business_fields

Business field categories for suppliers.

**Purpose:** Classify supplier business categories  
**Relationships:** Many-to-many with suppliers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Business field ID |
| name | VARCHAR(255) | NOT NULL | Field name: fertilizer, seeds, equipment |
| description | TEXT | | Field description |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

---

### representative_positions

Representative position types for suppliers.

**Purpose:** Define supplier representative roles  
**Relationships:** Many-to-many with suppliers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Position ID |
| name | VARCHAR(255) | NOT NULL | Position name: Sales Manager, Director |
| description | TEXT | | Position description |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

---

## eKYC Tables

### ekycs

Electronic Know Your Customer (eKYC) verification data.

**Purpose:** Store eKYC verification results  
**Relationships:** Belongs to one account (one-to-one)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | eKYC ID |
| account_id | BIGINT | NOT NULL, UNIQUE, FK(accounts.id) | Reference to account |
| id_number | VARCHAR(20) | | ID card number |
| full_name | VARCHAR(255) | | Full name from ID |
| date_of_birth | VARCHAR(50) | | Birth date from ID |
| gender | VARCHAR(20) | | Gender from ID |
| nationality | VARCHAR(50) | | Nationality |
| place_of_origin | VARCHAR(255) | | Place of origin |
| place_of_residence | TEXT | | Residential address |
| issue_date | VARCHAR(50) | | ID issue date |
| expiry_date | VARCHAR(50) | | ID expiry date |
| front_image_url | TEXT | | ID front image URL |
| back_image_url | TEXT | | ID back image URL |
| face_image_url | TEXT | | Face photo URL |
| img_near | TEXT | | Near face image |
| img_far | TEXT | | Far face image |
| is_verify | BOOLEAN | DEFAULT FALSE | Verification status |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_ekycs_account_id` on account_id UNIQUE
- `idx_ekycs_id_number` on id_number
- `idx_ekycs_is_verify` on is_verify

---

### frm_farmers

FRM (Farmer Registration Module) system integration data.

**Purpose:** Store data from external FRM system  
**Relationships:** Belongs to one account

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | FRM farmer ID |
| account_id | BIGINT | FK(accounts.id) | Reference to account |
| contact_id | VARCHAR(255) | | Contact ID from FRM |
| customer_code | VARCHAR(50) | | Customer code from FRM |
| full_name | VARCHAR(255) | | Full name |
| first_name | VARCHAR(255) | | First name |
| gender | VARCHAR(20) | | Gender |
| birth_year | INT | | Birth year |
| occupation | VARCHAR(100) | | Occupation |
| marital_status | VARCHAR(50) | | Marital status |
| id_card_number | VARCHAR(20) | | ID card number |
| id_card_issue_place | VARCHAR(255) | | ID issue place |
| phone | VARCHAR(20) | | Phone number |
| permanent_address | TEXT | | Permanent address |
| temporary_address | TEXT | | Temporary address |
| customer_type | VARCHAR(100) | | Customer type |
| bu_code | VARCHAR(50) | | Business unit code |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

---

## Authorization Tables

### casbin_rule

Casbin RBAC policy rules.

**Purpose:** Store Casbin authorization policies  
**Relationships:** None (policy engine data)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Rule ID |
| ptype | VARCHAR(100) | | Policy type: p, g |
| v0 | VARCHAR(100) | | Subject (account_id or role) |
| v1 | VARCHAR(100) | | Domain (hub_code or *) |
| v2 | VARCHAR(100) | | Object (resource) |
| v3 | VARCHAR(100) | | Action (read, write) |
| v4 | VARCHAR(100) | | Reserved |
| v5 | VARCHAR(100) | | Reserved |

**Policy Types:**
- `p`: Permission (account_id, domain, resource, action)
- `g`: Grouping/Role (account_id, role, domain)

**Example:**
```sql
-- Assign role to account in hub
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES ('g', '123', 'farmer_manager', 'HUB001');

-- Grant permission
INSERT INTO casbin_rule (ptype, v0, v1, v2, v3) 
VALUES ('p', 'farmer_manager', 'HUB001', '/farmers', 'write');
```

---

### permissions

System permissions (gRPC endpoints).

**Purpose:** Store all available gRPC endpoints as permissions  
**Relationships:** Many-to-many with roles via role_permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Permission ID |
| endpoint | VARCHAR(255) | NOT NULL, UNIQUE | gRPC endpoint path |
| service_name | VARCHAR(100) | NOT NULL | Service name: auth.v1.AuthService |
| method_name | VARCHAR(100) | NOT NULL | Method name: Login |
| description | TEXT | | Permission description |

**Unique Constraint:**
- `UNIQUE(service_name, method_name)`

**Example:**
```sql
INSERT INTO permissions (endpoint, service_name, method_name, description) 
VALUES ('/auth.v1.AuthService/Login', 'auth.v1.AuthService', 'Login', 'User login endpoint');
```

---

### roles

System roles for RBAC.

**Purpose:** Define user roles  
**Relationships:** 
- Many-to-many with accounts via casbin_rule
- Many-to-many with permissions via role_permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Role ID |
| code | VARCHAR(50) | NOT NULL, UNIQUE | Role code (unix nanosecond) |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Role name: Administrator |
| description | TEXT | | Role description |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Example:**
```sql
INSERT INTO roles (code, name, description) 
VALUES ('admin', 'Administrator', 'Full system access');
```

---

### role_permissions

Junction table linking roles to permissions.

**Purpose:** Associate permissions with roles  
**Relationships:** Junction between roles and permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Junction ID |
| role_id | BIGINT | NOT NULL, FK(roles.id) | Reference to role |
| permission_id | BIGINT | NOT NULL, FK(permissions.id) | Reference to permission |

**Unique Constraint:**
- `UNIQUE(role_id, permission_id)`

---

## Hub Management Tables

### farmer_hubs

Farmer hub assignments.

**Purpose:** Assign farmers to hubs/locations  
**Relationships:** Belongs to account

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Hub assignment ID |
| account_id | BIGINT | NOT NULL, FK(accounts.id) | Reference to account |
| hub_code | VARCHAR(50) | NOT NULL | Hub code |
| hub_name | VARCHAR(255) | | Hub name |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_farmer_hubs_account_id` on account_id
- `idx_farmer_hubs_hub_code` on hub_code

---

### supplier_hubs

Supplier hub assignments.

**Purpose:** Assign suppliers to hubs/locations  
**Relationships:** Belongs to account

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Hub assignment ID |
| account_id | BIGINT | NOT NULL, FK(accounts.id) | Reference to account |
| hub_code | VARCHAR(50) | NOT NULL | Hub code |
| hub_name | VARCHAR(255) | | Hub name |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_supplier_hubs_account_id` on account_id
- `idx_supplier_hubs_hub_code` on hub_code

---

## Consent Management Tables

### consent_policies

Consent policy definitions for GDPR/data privacy compliance.

**Purpose:** Define consent policies  
**Relationships:** Has many consent_logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Policy ID |
| code | VARCHAR(50) | NOT NULL, UNIQUE | Policy code |
| title | VARCHAR(255) | NOT NULL | Policy title |
| description | TEXT | | Policy description |
| content | TEXT | | Policy full content |
| version | VARCHAR(20) | | Policy version |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

---

### consent_logs

User consent logs.

**Purpose:** Track user consents for audit trail  
**Relationships:** 
- Belongs to account
- References consent_policy

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Consent log ID |
| account_id | BIGINT | NOT NULL, FK(accounts.id) | Reference to account |
| policy_code | VARCHAR(50) | NOT NULL, FK(consent_policies.code) | Policy code |
| consent_given | BOOLEAN | NOT NULL | Consent status |
| ip_address | VARCHAR(45) | | User IP address |
| user_agent | TEXT | | Browser/app user agent |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Consent timestamp |

**Indexes:**
- `idx_consent_logs_account_id` on account_id
- `idx_consent_logs_policy_code` on policy_code

---

## Audit Tables

### audit_logs

System audit trail for all critical operations.

**Purpose:** Track all important system events  
**Relationships:** References accounts for actions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Audit log ID |
| entity_type | VARCHAR(100) | NOT NULL | Entity: account, farmer, role |
| entity_id | BIGINT | | Entity ID |
| action | VARCHAR(50) | NOT NULL | Action: create, update, delete |
| action_by | BIGINT | FK(accounts.id) | Account who performed action |
| old_values | JSONB | | Previous values (JSON) |
| new_values | JSONB | | New values (JSON) |
| ip_address | VARCHAR(45) | | IP address |
| user_agent | TEXT | | User agent |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Event timestamp |

**Indexes:**
- `idx_audit_logs_entity_type` on entity_type
- `idx_audit_logs_entity_id` on entity_id
- `idx_audit_logs_action_by` on action_by
- `idx_audit_logs_created_at` on created_at DESC

**Example:**
```sql
INSERT INTO audit_logs (entity_type, entity_id, action, action_by, new_values) 
VALUES ('account', 123, 'create', 1, '{"name": "John Doe"}');
```

---

## Database Triggers

### Updated At Triggers

All tables have automatic `updated_at` triggers:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_accounts_updated_at
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Indexes Strategy

### Primary Indexes

All foreign keys have indexes:
- `accounts.user_id`
- `farmers.account_id`
- `suppliers.account_id`
- `refresh_tokens.account_id`
- `device_sessions.account_id`

### Composite Indexes

For filtering operations:
- `idx_accounts_source_type` on (source, type)
- `idx_accounts_is_ekyc_is_deleted` on (is_ekyc, is_deleted)
- `idx_farmers_status_is_deleted` on (status, is_deleted)
- `idx_suppliers_status_is_deleted` on (status, is_deleted)

### Soft Delete Indexes

All tables with soft delete:
- `idx_{table}_is_deleted` on is_deleted

---

## Migration History

### Key Migrations

| Migration | Version | Description |
|-----------|---------|-------------|
| Initial Schema | 001-011 | Core tables (users, accounts, tokens, OTP, Casbin, devices) |
| Domain Models | 007-008, 019-027 | Farmers, suppliers, eKYC, parcel lands |
| FRM Integration | 024, 028, 034 | FRM farmers table and flags |
| Consent Management | 029, 047-048 | Consent logs and policies |
| Account Enhancements | 031-033, 041, 058, 062, 067 | Source, flags, code, active status |
| RBAC System | 050-053 | Permissions, roles, role_permissions |
| Hub Management | 055-056, 059, 068 | Farmer hubs, supplier hubs |
| Audit Trail | 069-070 | Audit logs with action tracking |

### Schema Evolution

The database has evolved through 70+ migrations:
1. **Phase 1 (001-011):** Core authentication infrastructure
2. **Phase 2 (012-018):** Relationship restructuring and cleanup
3. **Phase 3 (019-027):** eKYC and farmer domain expansion
4. **Phase 4 (028-048):** FRM integration, consent management
5. **Phase 5 (050-070):** RBAC system, hubs, audit trail

---

## Query Examples

### Find Account with All Relationships

```sql
SELECT 
    a.*,
    u.name as user_name,
    u.date_of_birth,
    f.id as farmer_id,
    f.customer_code,
    s.id as supplier_id,
    s.company_name,
    e.id_number as ekyc_id_number
FROM accounts a
LEFT JOIN users u ON a.user_id = u.id
LEFT JOIN farmers f ON a.id = f.account_id
LEFT JOIN suppliers s ON a.id = s.account_id
LEFT JOIN ekycs e ON a.id = e.account_id
WHERE a.id = 123 AND a.is_deleted = FALSE;
```

### Get Farmer with Parcel Lands

```sql
SELECT 
    f.*,
    a.identifier,
    COUNT(pl.id) as parcel_count,
    SUM(pl.area) as total_area
FROM farmers f
JOIN accounts a ON f.account_id = a.id
LEFT JOIN parcel_lands pl ON f.id = pl.farmer_id AND pl.is_deleted = FALSE
WHERE f.account_id = 123 AND f.is_deleted = FALSE
GROUP BY f.id, a.identifier;
```

### Get Account Permissions via Casbin

```sql
-- Get roles for account in a hub
SELECT DISTINCT v1 as role
FROM casbin_rule
WHERE ptype = 'g' 
  AND v0 = '123'  -- account_id
  AND v2 IN ('HUB001', '*');

-- Get permissions for role in hub
SELECT DISTINCT v2 as resource, v3 as action
FROM casbin_rule
WHERE ptype = 'p'
  AND v0 = 'farmer_manager'
  AND v1 IN ('HUB001', '*');
```

### List Accounts with Filters (Strapi-style)

```sql
-- Example: Get active farmers from app source
SELECT a.*
FROM accounts a
WHERE a.source = 'app'
  AND a.is_farmer = TRUE
  AND a.is_active_farmer = TRUE
  AND a.is_deleted = FALSE
ORDER BY a.created_at DESC
LIMIT 20 OFFSET 0;
```

---

## Database Maintenance

### Soft Delete Cleanup

Clean up old soft-deleted records:

```sql
-- Find old deleted records (>90 days)
SELECT entity_type, COUNT(*) 
FROM (
    SELECT 'accounts' as entity_type, created_at 
    FROM accounts WHERE is_deleted = TRUE
    UNION ALL
    SELECT 'farmers', created_at 
    FROM farmers WHERE is_deleted = TRUE
) AS deleted_records
WHERE created_at < NOW() - INTERVAL '90 days'
GROUP BY entity_type;

-- Permanently delete (use with caution)
DELETE FROM accounts 
WHERE is_deleted = TRUE 
  AND created_at < NOW() - INTERVAL '90 days';
```

### Token Cleanup

Remove expired refresh tokens:

```sql
DELETE FROM refresh_tokens 
WHERE expires_at < NOW() 
  OR is_revoked = TRUE;
```

### OTP Cleanup

Remove old OTP records:

```sql
DELETE FROM otp_verifications 
WHERE created_at < NOW() - INTERVAL '24 hours';
```

---

## Backup Strategy

### Daily Backups

```bash
# Full database backup
pg_dump -U postgres -d centre_auth -F c -f backup_$(date +%Y%m%d).dump

# Schema only backup
pg_dump -U postgres -d centre_auth -s -f schema_$(date +%Y%m%d).sql

# Data only backup
pg_dump -U postgres -d centre_auth -a -f data_$(date +%Y%m%d).sql
```

### Restore

```bash
# Restore full backup
pg_restore -U postgres -d centre_auth backup_20251218.dump

# Restore from SQL
psql -U postgres -d centre_auth -f schema_20251218.sql
```

---

## Performance Tuning

### Connection Pooling

```yaml
# config/config.yaml
database:
  max_open_conns: 25
  max_idle_conns: 5
  conn_max_lifetime: 5m
```

### Query Optimization

1. **Use indexes** for filtering columns
2. **Avoid N+1 queries** - use JOINs or eager loading
3. **Limit result sets** with pagination
4. **Use prepared statements** for repeated queries
5. **Monitor slow queries** with `pg_stat_statements`

### Analyze Tables

```sql
ANALYZE accounts;
ANALYZE farmers;
ANALYZE suppliers;
```

---

## Navigation

### Documentation Home
- [Back to README](../../README.md) - Main documentation hub

### Related Documentation
- [Architecture Overview](../architecture/overview.md) - System design and components
- [API Reference](../api/api_reference.md) - Complete API documentation
- [Testing Guide](../guides/testing_guide.md) - Testing procedures
- [Deployment Guide](../guides/deployment_guide.md) - Production deployment

### Project Documentation
- [CHANGELOG](../../CHANGELOG.md) - Version history and updates
- [Port Allocation](../../../docs/PORT_ALLOCATION.md) - System-wide port assignments

**Version**: 1.0.0 | [Back to Top](#centre-auth-service-database-schema)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-18 | Initial schema documentation from 70+ migrations |
