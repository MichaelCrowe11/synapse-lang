-- Synapse Language Payment Database Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Licenses table
CREATE TABLE licenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_key VARCHAR(32) UNIQUE NOT NULL,
    charge_id VARCHAR(255) UNIQUE NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    price_paid_usd DECIMAL(10, 2) NOT NULL,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Payments table for tracking charge history
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    charge_id VARCHAR(255) UNIQUE NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    amount_usd DECIMAL(10, 2) NOT NULL,
    currency_paid VARCHAR(10), -- BTC, ETH, etc.
    amount_paid DECIMAL(20, 8), -- Amount in crypto
    status VARCHAR(20) NOT NULL, -- pending, confirmed, failed, expired
    coinbase_code VARCHAR(255), -- Coinbase charge code
    hosted_url TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Email logs table
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipient_email VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- license_delivery, payment_confirmation, etc.
    subject VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed, bounced
    license_key VARCHAR(32),
    charge_id VARCHAR(255),
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Webhook events table for debugging
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    charge_id VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processing_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX idx_licenses_email ON licenses(customer_email);
CREATE INDEX idx_licenses_key ON licenses(license_key);
CREATE INDEX idx_licenses_active ON licenses(active, expires_at);
CREATE INDEX idx_payments_email ON payments(customer_email);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_charge_id ON payments(charge_id);
CREATE INDEX idx_webhook_events_charge_id ON webhook_events(charge_id);
CREATE INDEX idx_webhook_events_processed ON webhook_events(processed, created_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_licenses_updated_at BEFORE UPDATE ON licenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (remove in production)
INSERT INTO licenses (
    license_key, charge_id, product_type, product_name, 
    customer_email, customer_name, price_paid_usd, expires_at
) VALUES (
    'SYN-SAMPLE123456', 'test_charge_123', 'professional', 
    'Synapse Language Professional', 'test@example.com', 
    'Test User', 499.00, CURRENT_TIMESTAMP + INTERVAL '1 year'
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;