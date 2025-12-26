#!/bin/bash
# =============================================================================
# Database Initialization Script for CAS (Centre Auth Service)
# =============================================================================
# This script runs automatically after 01_create_databases.sql
# It creates the complete schema for centre_auth database
# =============================================================================

set -e

echo "=========================================="
echo "Initializing CAS Database Schema..."
echo "=========================================="

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "centre_auth" <<-EOSQL

-- =====================================================
-- CONSOLIDATED SCHEMA MIGRATION FOR CAS
-- =====================================================

BEGIN;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Trigger functions
CREATE OR REPLACE FUNCTION public.update_ekycs_updated_at() RETURNS trigger
    LANGUAGE plpgsql AS \$\$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
\$\$;

CREATE OR REPLACE FUNCTION public.update_roles_updated_at() RETURNS trigger
    LANGUAGE plpgsql AS \$\$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
\$\$;

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

-- accounts table
CREATE TABLE IF NOT EXISTS public.accounts (
    id bigint NOT NULL,
    type text NOT NULL,
    identifier text NOT NULL,
    password_hash text,
    provider text,
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    source text NOT NULL,
    is_ekyc boolean DEFAULT false NOT NULL,
    is_farmer boolean DEFAULT false NOT NULL,
    is_form boolean DEFAULT false NOT NULL,
    is_supplier boolean DEFAULT false NOT NULL,
    is_deactive boolean DEFAULT false NOT NULL,
    is_frm_farmer boolean DEFAULT false NOT NULL,
    is_active_farmer boolean DEFAULT true NOT NULL,
    is_active_supplier boolean DEFAULT true NOT NULL,
    CONSTRAINT accounts_source_check CHECK ((source = ANY (ARRAY['app'::text, 'web'::text]))),
    CONSTRAINT check_accounts_identifier_not_empty CHECK ((length(TRIM(BOTH FROM identifier)) > 0)),
    CONSTRAINT check_accounts_type_valid CHECK ((type = ANY (ARRAY['email'::text, 'phone'::text, 'sso'::text])))
);

CREATE SEQUENCE IF NOT EXISTS public.accounts_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.accounts_id_seq OWNED BY public.accounts.id;
ALTER TABLE ONLY public.accounts ALTER COLUMN id SET DEFAULT nextval('public.accounts_id_seq'::regclass);
ALTER TABLE ONLY public.accounts ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.accounts ADD CONSTRAINT accounts_type_identifier_key UNIQUE (type, identifier);

-- users table
CREATE TABLE IF NOT EXISTS public.users (
    id bigint NOT NULL,
    name character varying(100),
    date_of_birth date,
    gender character varying(20),
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    account_id bigint,
    phone character varying(20),
    email character varying(255),
    address text
);

CREATE SEQUENCE IF NOT EXISTS public.users_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
ALTER TABLE ONLY public.users ADD CONSTRAINT users_pkey PRIMARY KEY (id);

-- device_sessions table (critical for FCM)
CREATE TABLE IF NOT EXISTS public.device_sessions (
    id bigint NOT NULL,
    account_id bigint NOT NULL,
    firebase_token text,
    device_id text,
    device_type text,
    device_name text,
    os_version text,
    app_version text,
    ip_address text,
    user_agent text,
    last_active_at timestamp without time zone DEFAULT now() NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.device_sessions_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.device_sessions_id_seq OWNED BY public.device_sessions.id;
ALTER TABLE ONLY public.device_sessions ALTER COLUMN id SET DEFAULT nextval('public.device_sessions_id_seq'::regclass);
ALTER TABLE ONLY public.device_sessions ADD CONSTRAINT device_sessions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.device_sessions ADD CONSTRAINT device_sessions_account_id_device_id_key UNIQUE (account_id, device_id);

-- suppliers table
CREATE TABLE IF NOT EXISTS public.suppliers (
    id bigint NOT NULL,
    account_id bigint,
    company_name character varying(200),
    tax_code character varying(50),
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    business_field text[],
    business_id text,
    representative_name text,
    representative_position text,
    img_back_url text,
    img_front_url text,
    data_url jsonb,
    activity_type text,
    representative_card_number text,
    company_address jsonb,
    operation_area jsonb,
    representative_address jsonb,
    crop_type_supported text[],
    cultivation_service_type text[],
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    denied_reason text,
    is_active_supplier boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_suppliers_status CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'approved'::character varying, 'denied'::character varying])::text[])))
);

CREATE SEQUENCE IF NOT EXISTS public.suppliers_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.suppliers_id_seq OWNED BY public.suppliers.id;
ALTER TABLE ONLY public.suppliers ALTER COLUMN id SET DEFAULT nextval('public.suppliers_id_seq'::regclass);
ALTER TABLE ONLY public.suppliers ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.suppliers ADD CONSTRAINT suppliers_account_id_key UNIQUE (account_id);

-- farmers table
CREATE TABLE IF NOT EXISTS public.farmers (
    id bigint NOT NULL,
    account_id bigint NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    customer_code text,
    avarta_url text,
    investment_area text,
    agricultural_officer text,
    area numeric(10,2),
    cultivated_area jsonb,
    crop_types text[],
    investment_zone text,
    investment_programs text[],
    customer_type text,
    customer_group text,
    img_front_url text,
    img_back_url text,
    status text,
    is_skip boolean DEFAULT false,
    is_contact boolean DEFAULT false
);

CREATE SEQUENCE IF NOT EXISTS public.farmers_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.farmers_id_seq OWNED BY public.farmers.id;
ALTER TABLE ONLY public.farmers ALTER COLUMN id SET DEFAULT nextval('public.farmers_id_seq'::regclass);
ALTER TABLE ONLY public.farmers ADD CONSTRAINT farmers_pkey PRIMARY KEY (id);

-- refresh_tokens table
CREATE TABLE IF NOT EXISTS public.refresh_tokens (
    id bigint NOT NULL,
    account_id bigint NOT NULL,
    token text NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    is_revoked boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.refresh_tokens_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;
ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);
ALTER TABLE ONLY public.refresh_tokens ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.refresh_tokens ADD CONSTRAINT refresh_tokens_token_key UNIQUE (token);

-- otp_verifications table
CREATE TABLE IF NOT EXISTS public.otp_verifications (
    phone_number character varying(20) NOT NULL,
    otp_code character varying(6) NOT NULL,
    purpose character varying(20) NOT NULL,
    chat_id character varying(50),
    is_verified boolean DEFAULT false,
    is_used boolean DEFAULT false,
    expires_at timestamp without time zone NOT NULL,
    verified_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);

ALTER TABLE ONLY public.otp_verifications ADD CONSTRAINT otp_verifications_pkey PRIMARY KEY (id);

-- roles table
CREATE TABLE IF NOT EXISTS public.roles (
    id bigint NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.roles_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;
ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);
ALTER TABLE ONLY public.roles ADD CONSTRAINT roles_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.roles ADD CONSTRAINT roles_code_key UNIQUE (code);
ALTER TABLE ONLY public.roles ADD CONSTRAINT roles_name_unique UNIQUE (name);

-- permissions table
CREATE TABLE IF NOT EXISTS public.permissions (
    id bigint NOT NULL,
    endpoint character varying(255) NOT NULL,
    service_name character varying(100) NOT NULL,
    method_name character varying(100) NOT NULL,
    description text
);

CREATE SEQUENCE IF NOT EXISTS public.permissions_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;
ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);
ALTER TABLE ONLY public.permissions ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.permissions ADD CONSTRAINT permissions_endpoint_key UNIQUE (endpoint);

-- role_permissions table
CREATE TABLE IF NOT EXISTS public.role_permissions (
    id bigint NOT NULL,
    role_id bigint NOT NULL,
    permission_id bigint NOT NULL
);

CREATE SEQUENCE IF NOT EXISTS public.role_permissions_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.role_permissions_id_seq OWNED BY public.role_permissions.id;
ALTER TABLE ONLY public.role_permissions ALTER COLUMN id SET DEFAULT nextval('public.role_permissions_id_seq'::regclass);
ALTER TABLE ONLY public.role_permissions ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.role_permissions ADD CONSTRAINT unique_role_permission UNIQUE (role_id, permission_id);

-- casbin_rule table
CREATE TABLE IF NOT EXISTS public.casbin_rule (
    id bigint NOT NULL,
    ptype character varying(100),
    v0 character varying(100),
    v1 character varying(100),
    v2 character varying(100),
    v3 character varying(100),
    v4 character varying(100),
    v5 character varying(100)
);

CREATE SEQUENCE IF NOT EXISTS public.casbin_rule_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.casbin_rule_id_seq OWNED BY public.casbin_rule.id;
ALTER TABLE ONLY public.casbin_rule ALTER COLUMN id SET DEFAULT nextval('public.casbin_rule_id_seq'::regclass);
ALTER TABLE ONLY public.casbin_rule ADD CONSTRAINT casbin_rule_pkey PRIMARY KEY (id);

-- ekycs table
CREATE TABLE IF NOT EXISTS public.ekycs (
    id bigint NOT NULL,
    account_id integer NOT NULL,
    img text,
    img_back text,
    img_front text,
    img_near text,
    img_far text,
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    mrz text,
    face_image text,
    card_number character varying(50),
    date_of_birth character varying(20),
    issue_date character varying(20),
    previous_number character varying(20),
    name character varying(255),
    sex character varying(10),
    nationality character varying(100),
    nation character varying(100),
    religion character varying(100),
    hometown text,
    address text,
    "character" text,
    expired_date character varying(20),
    father_name character varying(255),
    mother_name character varying(255),
    partner_name character varying(255),
    is_verified boolean DEFAULT false NOT NULL,
    img_far_url text,
    img_front_url text,
    img_back_url text
);

CREATE SEQUENCE IF NOT EXISTS public.ekycs_id_seq START WITH 1 INCREMENT BY 1;
ALTER SEQUENCE public.ekycs_id_seq OWNED BY public.ekycs.id;
ALTER TABLE ONLY public.ekycs ALTER COLUMN id SET DEFAULT nextval('public.ekycs_id_seq'::regclass);
ALTER TABLE ONLY public.ekycs ADD CONSTRAINT ekycs_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.ekycs ADD CONSTRAINT ekycs_account_id_key UNIQUE (account_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_accounts_type ON public.accounts(type);
CREATE INDEX IF NOT EXISTS idx_accounts_identifier ON public.accounts(identifier);
CREATE INDEX IF NOT EXISTS idx_device_sessions_account_id ON public.device_sessions(account_id);
CREATE INDEX IF NOT EXISTS idx_device_sessions_device_id ON public.device_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_device_sessions_firebase_token ON public.device_sessions(firebase_token);
CREATE INDEX IF NOT EXISTS idx_device_sessions_is_active ON public.device_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_suppliers_account_id ON public.suppliers(account_id);
CREATE INDEX IF NOT EXISTS idx_farmers_account_id ON public.farmers(account_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_account_id ON public.refresh_tokens(account_id);
CREATE INDEX IF NOT EXISTS idx_users_account_id ON public.users(account_id);

-- Triggers
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON public.accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_device_sessions_updated_at BEFORE UPDATE ON public.device_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON public.suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_farmers_updated_at BEFORE UPDATE ON public.farmers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_refresh_tokens_updated_at BEFORE UPDATE ON public.refresh_tokens FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON public.roles FOR EACH ROW EXECUTE FUNCTION update_roles_updated_at();
CREATE TRIGGER update_ekycs_updated_at BEFORE UPDATE ON public.ekycs FOR EACH ROW EXECUTE FUNCTION update_ekycs_updated_at();

-- Foreign Keys
ALTER TABLE ONLY public.device_sessions ADD CONSTRAINT device_sessions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.suppliers ADD CONSTRAINT suppliers_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE SET NULL;
ALTER TABLE ONLY public.farmers ADD CONSTRAINT farmers_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE SET NULL;
ALTER TABLE ONLY public.refresh_tokens ADD CONSTRAINT refresh_tokens_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.users ADD CONSTRAINT users_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.ekycs ADD CONSTRAINT ekycs_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.role_permissions ADD CONSTRAINT fk_permission FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.role_permissions ADD CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;

COMMIT;

EOSQL

echo "=========================================="
echo "CAS Database Schema initialized!"
echo "=========================================="
