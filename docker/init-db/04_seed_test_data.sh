#!/bin/bash
# =============================================================================
# Seed Test Data for TOB-37 and TOB-45 Testing
# =============================================================================
# This script inserts test data for FCM notification testing
# 
# IMPORTANT: After running docker-compose, you need to update the firebase_token
# with a real FCM token from the mobile app!
# =============================================================================

set -e

echo "=========================================="
echo "Seeding Test Data..."
echo "=========================================="

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "centre_auth" <<-EOSQL

-- =====================================================
-- TEST DATA FOR TOB-37/TOB-45 TESTING
-- =====================================================

BEGIN;

-- Create test account
INSERT INTO accounts (id, type, identifier, password_hash, source, is_supplier, is_active_supplier, created_at, updated_at)
VALUES (
    999,
    'phone',
    '0909999999',
    '\$2a\$10\$dummy.hash.for.testing.only',  -- Not a real hash, just for testing
    'app',
    true,
    true,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO UPDATE SET 
    is_supplier = true, 
    is_active_supplier = true,
    updated_at = NOW();

-- Create test user
INSERT INTO users (id, name, phone, account_id, created_at, updated_at)
VALUES (
    999,
    'Test Supplier User',
    '0909999999',
    999,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    updated_at = NOW();

-- Create test supplier linked to account
INSERT INTO suppliers (id, account_id, company_name, status, is_active_supplier, is_deleted, created_at, updated_at)
VALUES (
    888,
    999,
    'Test Supplier Company',
    'approved',
    true,
    false,
    NOW(),
    NOW()
)
ON CONFLICT (id) DO UPDATE SET 
    is_active_supplier = true,
    status = 'approved',
    updated_at = NOW();

-- Create device session with placeholder FCM token
-- IMPORTANT: Update this token with real FCM token from mobile app!
INSERT INTO device_sessions (id, account_id, device_id, firebase_token, device_type, device_name, is_active, created_at, updated_at)
VALUES (
    1,
    999,
    'test-device-001',
    'PLACEHOLDER_FCM_TOKEN_UPDATE_WITH_REAL_TOKEN',  -- UPDATE THIS!
    'android',
    'Test Device for TOB-37/TOB-45',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (account_id, device_id) DO UPDATE SET 
    firebase_token = EXCLUDED.firebase_token,
    is_active = true,
    updated_at = NOW();

COMMIT;

EOSQL

echo "=========================================="
echo "Test Data Seeded!"
echo ""
echo "IMPORTANT: Update the firebase_token in device_sessions table"
echo "with a real FCM token from the mobile app before testing!"
echo ""
echo "Run this SQL after getting FCM token from mobile app:"
echo "  UPDATE device_sessions SET firebase_token = 'YOUR_REAL_FCM_TOKEN' WHERE account_id = 999;"
echo "=========================================="
