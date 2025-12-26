#!/bin/bash
# =============================================================================
# Supplier Service Database Schema Initialization
# =============================================================================
# This script creates the agrios schema and tables for supplier-service.
# It runs automatically as part of PostgreSQL initialization.
# =============================================================================

set -e

echo "=========================================="
echo "Initializing Supplier Service database..."
echo "=========================================="

# Connect to supplier_svc_db and create schema + tables
PGPASSWORD=postgres psql -h localhost -U postgres -d supplier_svc_db <<'EOSQL'

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS agrios;

-- Set search path
SET search_path TO agrios, public;

-- =============================================================================
-- Create enum types
-- =============================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'plant_type' AND typnamespace = 'agrios'::regnamespace) THEN
        CREATE TYPE agrios.plant_type AS ENUM ('Mía', 'Chuối', 'Dừa', 'Lứa');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stage_type' AND typnamespace = 'agrios'::regnamespace) THEN
        CREATE TYPE agrios.stage_type AS ENUM ('Chuẩn bị đất', 'Trồng trọt', 'Chăm sóc', 'Thu hoạch');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'unit_name' AND typnamespace = 'agrios'::regnamespace) THEN
        CREATE TYPE agrios.unit_name AS ENUM ('Diện tích', 'Khối lượng', 'Khoảng cách', 'Số lượng');
    END IF;
END$$;

-- =============================================================================
-- Create plant_types table
-- =============================================================================
CREATE TABLE IF NOT EXISTS agrios.plant_types (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL CHECK (LENGTH(name) > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_plant_types_name ON agrios.plant_types(name);
CREATE INDEX IF NOT EXISTS idx_plant_types_created_at ON agrios.plant_types(created_at DESC);

COMMENT ON TABLE agrios.plant_types IS 'Bảng quản lý loại cây trồng';

-- =============================================================================
-- Create stages table
-- =============================================================================
CREATE TABLE IF NOT EXISTS agrios.stages (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL CHECK (LENGTH(name) > 0),
    display_order INT DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stages_name ON agrios.stages(name);
CREATE INDEX IF NOT EXISTS idx_stages_created_at ON agrios.stages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_stages_is_active ON agrios.stages(is_active);

COMMENT ON TABLE agrios.stages IS 'Bảng quản lý giai đoạn canh tác';

-- =============================================================================
-- Create units table
-- =============================================================================
CREATE TABLE IF NOT EXISTS agrios.units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL CHECK (LENGTH(name) > 0),
    type TEXT[] NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_units_name ON agrios.units(name);
CREATE INDEX IF NOT EXISTS idx_units_created_at ON agrios.units(created_at DESC);

COMMENT ON TABLE agrios.units IS 'Bảng quản lý đơn vị tính';

-- =============================================================================
-- Create services table
-- =============================================================================
CREATE TABLE IF NOT EXISTS agrios.services (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL CHECK (LENGTH(name) > 0),
    code VARCHAR(8) NOT NULL UNIQUE CHECK (LENGTH(code) = 8),
    item_code VARCHAR(100),
    stage agrios.stage_type NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    plant_type agrios.plant_type NOT NULL,
    unit agrios.unit_name NOT NULL,
    unit_type VARCHAR(50) NOT NULL,
    method SMALLINT NOT NULL CHECK (method IN (1, 2)),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_services_code ON agrios.services(code);
CREATE INDEX IF NOT EXISTS idx_services_item_code ON agrios.services(item_code);
CREATE INDEX IF NOT EXISTS idx_services_is_active ON agrios.services(is_active);
CREATE INDEX IF NOT EXISTS idx_services_created_at ON agrios.services(created_at DESC);

COMMENT ON TABLE agrios.services IS 'Bảng quản lý dịch vụ canh tác';

-- =============================================================================
-- Seed data for plant_types
-- =============================================================================
INSERT INTO agrios.plant_types (name) VALUES
    ('Mía'),
    ('Chuối'),
    ('Dừa'),
    ('Lúa')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Seed data for stages
-- =============================================================================
INSERT INTO agrios.stages (name, display_order, is_active) VALUES
    ('Chuẩn bị đất', 1, true),
    ('Trồng trọt', 2, true),
    ('Chăm sóc', 3, true),
    ('Thu hoạch', 4, true)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Seed data for units
-- =============================================================================
INSERT INTO agrios.units (name, type) VALUES
    ('Diện tích', ARRAY['m2', 'km2', 'ha', 'công']),
    ('Khối lượng', ARRAY['kg', 'tấn', 'g']),
    ('Khoảng cách', ARRAY['m', 'km', 'cm']),
    ('Số lượng', ARRAY['cây', 'bụi', 'hàng', 'luống'])
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Seed data for services (sample)
-- =============================================================================
INSERT INTO agrios.services (name, code, item_code, stage, is_active, plant_type, unit, unit_type, method, created_by, updated_by) VALUES
    ('Làm đất bằng máy cày', 'AS000001', 'LD001', 'Chuẩn bị đất', true, 'Mía', 'Diện tích', 'ha', 1, 'system', 'system'),
    ('Trồng mía thủ công', 'AS000002', 'TM001', 'Trồng trọt', true, 'Mía', 'Diện tích', 'ha', 2, 'system', 'system'),
    ('Bón phân NPK', 'AS000003', 'BP001', 'Chăm sóc', true, 'Mía', 'Khối lượng', 'kg', 1, 'system', 'system'),
    ('Thu hoạch mía cơ giới', 'AS000004', 'TH001', 'Thu hoạch', true, 'Mía', 'Diện tích', 'ha', 1, 'system', 'system')
ON CONFLICT (code) DO NOTHING;

\echo ''
\echo '=========================================='
\echo 'Supplier Service schema initialized!'
\echo '  - Schema: agrios'
\echo '  - Tables: plant_types, stages, units, services'
\echo '  - Seed data inserted'
\echo '=========================================='

EOSQL

echo "Supplier Service database initialization complete!"
