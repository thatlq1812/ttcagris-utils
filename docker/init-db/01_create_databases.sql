-- =============================================================================
-- PostgreSQL Initialization Script for AgriOS Development
-- =============================================================================
-- This script runs automatically when PostgreSQL container starts for the first time.
-- It creates all databases and their schemas.
--
-- Databases:
--   - centre_auth: CAS (Centre Auth Service) database
--   - notification_service: Notification Service database
--   - supplier_svc_db: Supplier Service database
-- =============================================================================

-- Create databases
CREATE DATABASE centre_auth;
CREATE DATABASE notification_service;
CREATE DATABASE supplier_svc_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE centre_auth TO postgres;
GRANT ALL PRIVILEGES ON DATABASE notification_service TO postgres;
GRANT ALL PRIVILEGES ON DATABASE supplier_svc_db TO postgres;

\echo '=========================================='
\echo 'Databases created successfully!'
\echo '  - centre_auth'
\echo '  - notification_service'
\echo '  - supplier_svc_db'
\echo '=========================================='
