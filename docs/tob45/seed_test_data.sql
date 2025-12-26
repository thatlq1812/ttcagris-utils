-- =============================================================================
-- TOB-45 Test Data Seeding Script
-- =============================================================================
-- Run this script after applying migrations to set up test data for 
-- DeactiveSupplier flow testing.
-- 
-- Usage:
--   cat docs/tob45/seed_test_data.sql | docker exec -i agrios_dev_postgres psql -U postgres -d centre_auth
--
-- Test Credentials:
--   Phone: 0909999999
--   Password: password123
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. Test Account (Supplier)
-- =============================================================================
-- Password hash is bcrypt of "password123"
INSERT INTO accounts (
    id, type, identifier, password_hash, source, 
    is_supplier, is_active_supplier, code
)
VALUES (
    999, 'phone', '0909999999', 
    '$2y$10$Gjw4QnR8fJJN2YlKnAZVDOBY0kBiIiv7OxmCMqanEEc6JECVE3hp2', 
    'app', true, true, 'TEST001'
)
ON CONFLICT (id) DO UPDATE SET 
    password_hash = EXCLUDED.password_hash,
    is_supplier = EXCLUDED.is_supplier,
    is_active_supplier = EXCLUDED.is_active_supplier;

-- =============================================================================
-- 2. Test Supplier
-- =============================================================================
INSERT INTO suppliers (id, account_id, company_name, status)
VALUES (888, 999, 'Test Supplier Company', 'approved')
ON CONFLICT (id) DO UPDATE SET 
    account_id = EXCLUDED.account_id,
    status = EXCLUDED.status;

-- =============================================================================
-- 3. Test User Profile
-- =============================================================================
INSERT INTO users (id, account_id, name, phone)
VALUES (999, 999, 'Test Supplier User', '0909999999')
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    phone = EXCLUDED.phone;

-- =============================================================================
-- 4. Device Session (update firebase_token with real token from mobile app)
-- =============================================================================
INSERT INTO device_sessions (id, account_id, device_id, firebase_token, is_active)
VALUES (1, 999, 'test-device-001', 'PLACEHOLDER_UPDATE_WITH_REAL_FCM_TOKEN', true)
ON CONFLICT (id) DO UPDATE SET 
    firebase_token = EXCLUDED.firebase_token,
    is_active = EXCLUDED.is_active;

COMMIT;

-- =============================================================================
-- Verification queries
-- =============================================================================
SELECT 'Accounts:' as table_name, count(*) as count FROM accounts WHERE id = 999
UNION ALL
SELECT 'Suppliers:', count(*) FROM suppliers WHERE id = 888
UNION ALL
SELECT 'Users:', count(*) FROM users WHERE id = 999
UNION ALL
SELECT 'Device Sessions:', count(*) FROM device_sessions WHERE account_id = 999;

-- =============================================================================
-- To update FCM token after seeding:
-- =============================================================================
-- UPDATE device_sessions 
-- SET firebase_token = 'YOUR_REAL_FCM_TOKEN_FROM_MOBILE_APP' 
-- WHERE account_id = 999;
