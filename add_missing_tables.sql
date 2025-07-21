-- Add missing tables for brands and phone models

-- Brands table
CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    frame_color VARCHAR(50) DEFAULT '#000000',
    button_color VARCHAR(50) DEFAULT '#FFFFFF',
    is_available BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    subtitle VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phone models table
CREATE TABLE IF NOT EXISTS phone_models (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    name VARCHAR(200) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    chinese_model_id VARCHAR(100),
    price DECIMAL(10,2) DEFAULT 25.00,
    is_available BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates table (if not exists)
CREATE TABLE IF NOT EXISTS templates (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'basic',
    is_active BOOLEAN DEFAULT true,
    price DECIMAL(10,2) DEFAULT 25.00,
    display_price VARCHAR(50) DEFAULT '£25.00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_brands_available ON brands(is_available);
CREATE INDEX IF NOT EXISTS idx_brands_order ON brands(display_order);
CREATE INDEX IF NOT EXISTS idx_phone_models_brand ON phone_models(brand_id);
CREATE INDEX IF NOT EXISTS idx_phone_models_available ON phone_models(is_available);
CREATE INDEX IF NOT EXISTS idx_templates_active ON templates(is_active);

-- Insert default brands
INSERT INTO brands (name, display_name, frame_color, button_color, is_available, display_order, subtitle) VALUES
('IPHONE', 'iPhone', '#000000', '#007AFF', true, 1, 'Apple iPhone Cases'),
('SAMSUNG', 'Samsung', '#1428A0', '#FFFFFF', true, 2, 'Samsung Galaxy Cases'),
('GOOGLE', 'Google', '#4285F4', '#FFFFFF', true, 3, 'Google Pixel Cases'),
('ONEPLUS', 'OnePlus', '#FF0000', '#FFFFFF', true, 4, 'OnePlus Cases'),
('XIAOMI', 'Xiaomi', '#FF6900', '#FFFFFF', true, 5, 'Xiaomi Cases'),
('HUAWEI', 'Huawei', '#FF0000', '#FFFFFF', true, 6, 'Huawei Cases')
ON CONFLICT (name) DO NOTHING;

-- Insert iPhone models
INSERT INTO phone_models (brand_id, name, display_name, chinese_model_id, price, is_available, display_order) VALUES
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 15 Pro Max', 'iPhone 15 Pro Max', 'iphone_15_pro_max', 25.00, true, 1),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 15 Pro', 'iPhone 15 Pro', 'iphone_15_pro', 25.00, true, 2),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 15 Plus', 'iPhone 15 Plus', 'iphone_15_plus', 25.00, true, 3),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 15', 'iPhone 15', 'iphone_15', 25.00, true, 4),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 14 Pro Max', 'iPhone 14 Pro Max', 'iphone_14_pro_max', 25.00, true, 5),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 14 Pro', 'iPhone 14 Pro', 'iphone_14_pro', 25.00, true, 6),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 14 Plus', 'iPhone 14 Plus', 'iphone_14_plus', 25.00, true, 7),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 14', 'iPhone 14', 'iphone_14', 25.00, true, 8),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 13 Pro Max', 'iPhone 13 Pro Max', 'iphone_13_pro_max', 25.00, true, 9),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 13 Pro', 'iPhone 13 Pro', 'iphone_13_pro', 25.00, true, 10),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 13 mini', 'iPhone 13 mini', 'iphone_13_mini', 25.00, true, 11),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 13', 'iPhone 13', 'iphone_13', 25.00, true, 12),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 12 Pro Max', 'iPhone 12 Pro Max', 'iphone_12_pro_max', 25.00, true, 13),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 12 Pro', 'iPhone 12 Pro', 'iphone_12_pro', 25.00, true, 14),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 12 mini', 'iPhone 12 mini', 'iphone_12_mini', 25.00, true, 15),
((SELECT id FROM brands WHERE name = 'IPHONE'), 'iPhone 12', 'iPhone 12', 'iphone_12', 25.00, true, 16)
ON CONFLICT DO NOTHING;

-- Insert Samsung models
INSERT INTO phone_models (brand_id, name, display_name, chinese_model_id, price, is_available, display_order) VALUES
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy S24 Ultra', 'Galaxy S24 Ultra', 'samsung_s24_ultra', 25.00, true, 1),
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy S24+', 'Galaxy S24+', 'samsung_s24_plus', 25.00, true, 2),
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy S24', 'Galaxy S24', 'samsung_s24', 25.00, true, 3),
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy S23 Ultra', 'Galaxy S23 Ultra', 'samsung_s23_ultra', 25.00, true, 4),
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy S23+', 'Galaxy S23+', 'samsung_s23_plus', 25.00, true, 5),
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy S23', 'Galaxy S23', 'samsung_s23', 25.00, true, 6),
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy Note 20 Ultra', 'Galaxy Note 20 Ultra', 'samsung_note20_ultra', 25.00, true, 7),
((SELECT id FROM brands WHERE name = 'SAMSUNG'), 'Galaxy A54', 'Galaxy A54', 'samsung_a54', 25.00, true, 8)
ON CONFLICT DO NOTHING;

-- Insert Google Pixel models
INSERT INTO phone_models (brand_id, name, display_name, chinese_model_id, price, is_available, display_order) VALUES
((SELECT id FROM brands WHERE name = 'GOOGLE'), 'Pixel 8 Pro', 'Pixel 8 Pro', 'google_pixel_8_pro', 25.00, true, 1),
((SELECT id FROM brands WHERE name = 'GOOGLE'), 'Pixel 8', 'Pixel 8', 'google_pixel_8', 25.00, true, 2),
((SELECT id FROM brands WHERE name = 'GOOGLE'), 'Pixel 7 Pro', 'Pixel 7 Pro', 'google_pixel_7_pro', 25.00, true, 3),
((SELECT id FROM brands WHERE name = 'GOOGLE'), 'Pixel 7', 'Pixel 7', 'google_pixel_7', 25.00, true, 4),
((SELECT id FROM brands WHERE name = 'GOOGLE'), 'Pixel 6 Pro', 'Pixel 6 Pro', 'google_pixel_6_pro', 25.00, true, 5),
((SELECT id FROM brands WHERE name = 'GOOGLE'), 'Pixel 6', 'Pixel 6', 'google_pixel_6', 25.00, true, 6)
ON CONFLICT DO NOTHING;

-- Insert default templates
INSERT INTO templates (id, name, description, category, is_active, price, display_price) VALUES
('classic', 'Classic', 'Clean and simple design', 'basic', true, 25.00, '£25.00'),
('2-in-1', '2-in-1', 'Two photos side by side', 'basic', true, 25.00, '£25.00'),
('3-in-1', '3-in-1', 'Three photos layout', 'basic', true, 25.00, '£25.00'),
('4-in-1', '4-in-1', 'Four photos grid', 'basic', true, 25.00, '£25.00'),
('film-strip', 'Film Strip', 'Film strip style layout', 'basic', true, 25.00, '£25.00'),
('retro-remix', 'Retro Remix', 'AI-powered retro style transformation', 'ai', true, 25.00, '£25.00'),
('cover-shoot', 'Cover Shoot', 'Magazine cover style transformation', 'ai', true, 25.00, '£25.00'),
('funny-toon', 'Funny Toon', 'Cartoon style transformation', 'ai', true, 25.00, '£25.00'),
('glitch-pro', 'Glitch Pro', 'Digital glitch effects', 'ai', true, 25.00, '£25.00'),
('footy-fan', 'Footy Fan', 'Football team style transformation', 'ai', true, 25.00, '£25.00')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema updated successfully!';
    RAISE NOTICE 'Added tables: brands, phone_models, templates';
    RAISE NOTICE 'Added % brands', (SELECT COUNT(*) FROM brands);
    RAISE NOTICE 'Added % phone models', (SELECT COUNT(*) FROM phone_models);
    RAISE NOTICE 'Added % templates', (SELECT COUNT(*) FROM templates);
END $$;