#!/bin/bash
# =============================================================================
# Database Initialization Script for Notification Service
# =============================================================================
# This script runs automatically after 02_cas_schema.sh
# It creates the schema for notification_service database
# =============================================================================

set -e

echo "=========================================="
echo "Initializing Notification Service Database Schema..."
echo "=========================================="

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "notification_service" <<-EOSQL

-- =====================================================
-- SCHEMA FOR NOTIFICATION SERVICE
-- =====================================================

BEGIN;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trigger function for updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS \$\$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
\$\$ LANGUAGE plpgsql;

-- notifications table
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    data JSONB,
    type VARCHAR(50) NOT NULL DEFAULT 'general',
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_account_id ON public.notifications(account_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON public.notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON public.notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON public.notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_account_unread ON public.notifications(account_id, is_read) WHERE is_read = FALSE;

-- notification_templates table
CREATE TABLE IF NOT EXISTS public.notification_templates (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    title_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'general',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notification_templates_code ON public.notification_templates(code);
CREATE INDEX IF NOT EXISTS idx_notification_templates_type ON public.notification_templates(type);

-- fcm_event_logs table (for audit/debugging FCM sends)
CREATE TABLE IF NOT EXISTS public.fcm_event_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_tokens TEXT[] NOT NULL,
    action_code VARCHAR(10) NOT NULL,
    model VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    success_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,
    failed_tokens TEXT[],
    sent_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fcm_event_logs_action_code ON public.fcm_event_logs(action_code);
CREATE INDEX IF NOT EXISTS idx_fcm_event_logs_model ON public.fcm_event_logs(model);
CREATE INDEX IF NOT EXISTS idx_fcm_event_logs_sent_at ON public.fcm_event_logs(sent_at DESC);

-- topic_subscriptions table
CREATE TABLE IF NOT EXISTS public.topic_subscriptions (
    id SERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL,
    topic VARCHAR(100) NOT NULL,
    subscribed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    unsubscribed_at TIMESTAMP WITHOUT TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE(account_id, topic)
);

CREATE INDEX IF NOT EXISTS idx_topic_subscriptions_account_id ON public.topic_subscriptions(account_id);
CREATE INDEX IF NOT EXISTS idx_topic_subscriptions_topic ON public.topic_subscriptions(topic);
CREATE INDEX IF NOT EXISTS idx_topic_subscriptions_is_active ON public.topic_subscriptions(is_active);

-- Triggers
CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON public.notifications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_templates_updated_at BEFORE UPDATE ON public.notification_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_topic_subscriptions_updated_at BEFORE UPDATE ON public.topic_subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;

EOSQL

echo "=========================================="
echo "Notification Service Database Schema initialized!"
echo "=========================================="
