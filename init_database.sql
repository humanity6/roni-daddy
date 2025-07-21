-- PimpMyCase Database Schema
-- Run this script to initialize your PostgreSQL database on Render

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Customer info
    customer_email VARCHAR(255),
    customer_phone VARCHAR(50),
    
    -- Product details
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    color VARCHAR(50),
    template_id VARCHAR(100) NOT NULL,
    template_name VARCHAR(200),
    
    -- Design
    design_image_url TEXT,
    custom_text TEXT,
    font_family VARCHAR(100),
    text_color VARCHAR(50),
    
    -- Pricing
    base_price DECIMAL(10,2),
    total_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    
    -- Payment
    stripe_session_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'pending',
    
    -- Order status
    order_status VARCHAR(50) DEFAULT 'processing',
    queue_position INTEGER,
    
    -- Chinese API integration
    chinese_order_id VARCHAR(255),
    chinese_status VARCHAR(100),
    tracking_number VARCHAR(255),
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- AI generations table
CREATE TABLE IF NOT EXISTS ai_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    template_id VARCHAR(100) NOT NULL,
    style_params JSONB NOT NULL,
    quality VARCHAR(20) DEFAULT 'low',
    image_size VARCHAR(20) DEFAULT '1024x1536',
    
    original_image_url TEXT,
    generated_image_url TEXT,
    generation_time_ms INTEGER,
    
    cost_estimate DECIMAL(10,4),
    tokens_used INTEGER,
    
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Admin users table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    role VARCHAR(50) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    
    permissions JSONB DEFAULT '["read", "write"]'::jsonb
);

-- Sessions table for user sessions
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Session data
    brand VARCHAR(100),
    model VARCHAR(100),
    color VARCHAR(50),
    template_id VARCHAR(100),
    uploaded_images JSONB DEFAULT '[]'::jsonb,
    ai_credits INTEGER DEFAULT 4,
    
    -- QR session tracking
    qr_session BOOLEAN DEFAULT false,
    device_info JSONB DEFAULT '{}'::jsonb,
    
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_orders_stripe_session ON orders(stripe_session_id);
CREATE INDEX IF NOT EXISTS idx_orders_updated_at ON orders(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_generations_created_at ON ai_generations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_generations_template ON ai_generations(template_id);
CREATE INDEX IF NOT EXISTS idx_ai_generations_success ON ai_generations(success);

CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_active ON admin_users(is_active);

CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_qr ON sessions(qr_session);

-- Insert default admin user
-- Password: admin123 (CHANGE THIS IN PRODUCTION!)
-- Password hash generated with bcrypt
INSERT INTO admin_users (username, email, password_hash, role, permissions) 
VALUES (
    'admin', 
    'admin@pimpmycase.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeVMsteww2XM7K.5u',
    'admin',
    '["read", "write", "admin"]'::jsonb
) 
ON CONFLICT (username) DO NOTHING;

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for orders table
CREATE TRIGGER update_orders_updated_at 
    BEFORE UPDATE ON orders 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for order analytics
CREATE OR REPLACE VIEW order_analytics AS
SELECT 
    DATE(created_at) as order_date,
    COUNT(*) as total_orders,
    COUNT(CASE WHEN payment_status = 'paid' THEN 1 END) as paid_orders,
    COUNT(CASE WHEN order_status = 'completed' THEN 1 END) as completed_orders,
    SUM(CASE WHEN payment_status = 'paid' THEN total_price ELSE 0 END) as revenue,
    template_id,
    brand
FROM orders 
GROUP BY DATE(created_at), template_id, brand
ORDER BY order_date DESC;

-- View for recent activity
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    'order' as activity_type,
    id as activity_id,
    created_at,
    order_status as status,
    CONCAT(brand, ' ', model) as description,
    total_price as amount
FROM orders
UNION ALL
SELECT 
    'generation' as activity_type,
    id as activity_id,
    created_at,
    CASE WHEN success THEN 'success' ELSE 'failed' END as status,
    template_id as description,
    cost_estimate as amount
FROM ai_generations
ORDER BY created_at DESC
LIMIT 50;

-- Insert some sample template pricing data
CREATE TABLE IF NOT EXISTS template_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(200) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    ai_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default pricing
INSERT INTO template_pricing (template_id, template_name, base_price, ai_price) VALUES
('classic', 'Classic Template', 15.99, 0.00),
('2-in-1', '2-in-1 Template', 15.99, 0.00),
('3-in-1', '3-in-1 Template', 15.99, 0.00),
('4-in-1', '4-in-1 Template', 15.99, 0.00),
('film-strip', 'Film Strip Template', 15.99, 0.00),
('retro-remix', 'Retro Remix AI', 19.99, 4.00),
('cover-shoot', 'Cover Shoot AI', 19.99, 4.00),
('funny-toon', 'Funny Toon AI', 19.99, 4.00),
('glitch-pro', 'Glitch Pro AI', 19.99, 4.00),
('footy-fan', 'Footy Fan AI', 19.99, 4.00)
ON CONFLICT (template_id) DO NOTHING;

-- Grant necessary permissions (for Render free tier)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pimpmycase_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pimpmycase_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO pimpmycase_user;

-- Display success message and basic stats
DO $$
BEGIN
    RAISE NOTICE 'Database schema initialized successfully!';
    RAISE NOTICE 'Tables created: orders, ai_generations, admin_users, sessions, template_pricing';
    RAISE NOTICE 'Default admin user created: username=admin, password=admin123';
    RAISE NOTICE 'IMPORTANT: Change the default admin password in production!';
END $$;