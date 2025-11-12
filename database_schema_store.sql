-- Schema for Store Module
-- Products, Shopping Cart, and Customer Orders

-- Table: products
-- Stores all available products in the store
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    price NUMERIC(18, 2) NOT NULL CHECK (price >= 0),
    image_url TEXT,
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: customer_orders
-- Stores orders created by customers through the store
CREATE TABLE IF NOT EXISTS customer_orders (
    customer_order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(50),
    shipping_address TEXT NOT NULL,
    shipping_city VARCHAR(100) NOT NULL,
    shipping_state VARCHAR(100),
    shipping_zip VARCHAR(20),
    shipping_country VARCHAR(100) NOT NULL,
    subtotal_amount NUMERIC(18, 2) NOT NULL CHECK (subtotal_amount >= 0),
    tax_amount NUMERIC(18, 2) NOT NULL CHECK (tax_amount >= 0),
    shipping_cost NUMERIC(18, 2) NOT NULL CHECK (shipping_cost >= 0),
    total_amount NUMERIC(18, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(50) DEFAULT 'simulated',
    payment_status VARCHAR(50) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    session_id VARCHAR(255)
);

-- Table: order_items
-- Stores individual items within each customer order
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    customer_order_id INTEGER NOT NULL REFERENCES customer_orders(customer_order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    product_name VARCHAR(255) NOT NULL,
    product_price NUMERIC(18, 2) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    subtotal NUMERIC(18, 2) NOT NULL CHECK (subtotal >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
CREATE INDEX IF NOT EXISTS idx_customer_orders_status ON customer_orders(status);
CREATE INDEX IF NOT EXISTS idx_customer_orders_email ON customer_orders(customer_email);
CREATE INDEX IF NOT EXISTS idx_customer_orders_date ON customer_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_customer_order ON order_items(customer_order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

-- Sample products to get started
INSERT INTO products (name, description, category, subcategory, price, image_url, stock_quantity) VALUES
('Laptop Pro 15"', 'High-performance laptop with 16GB RAM and 512GB SSD', 'Electronics', 'Computers', 1299.99, 'https://via.placeholder.com/300x300.png?text=Laptop', 50),
('Wireless Mouse', 'Ergonomic wireless mouse with precision tracking', 'Electronics', 'Accessories', 29.99, 'https://via.placeholder.com/300x300.png?text=Mouse', 200),
('USB-C Hub', 'Multi-port USB-C hub with HDMI and ethernet', 'Electronics', 'Accessories', 49.99, 'https://via.placeholder.com/300x300.png?text=USB+Hub', 150),
('Office Chair', 'Ergonomic office chair with lumbar support', 'Furniture', 'Office', 299.99, 'https://via.placeholder.com/300x300.png?text=Chair', 75),
('Standing Desk', 'Adjustable height standing desk', 'Furniture', 'Office', 499.99, 'https://via.placeholder.com/300x300.png?text=Desk', 30),
('Monitor 27"', '4K UHD monitor with HDR support', 'Electronics', 'Monitors', 399.99, 'https://via.placeholder.com/300x300.png?text=Monitor', 60),
('Mechanical Keyboard', 'RGB mechanical keyboard with blue switches', 'Electronics', 'Accessories', 89.99, 'https://via.placeholder.com/300x300.png?text=Keyboard', 120),
('Desk Lamp', 'LED desk lamp with adjustable brightness', 'Furniture', 'Lighting', 39.99, 'https://via.placeholder.com/300x300.png?text=Lamp', 100),
('Webcam HD', '1080p webcam with built-in microphone', 'Electronics', 'Accessories', 79.99, 'https://via.placeholder.com/300x300.png?text=Webcam', 80),
('Notebook Set', 'Premium notebook set with 3 notebooks', 'Stationery', 'Notebooks', 19.99, 'https://via.placeholder.com/300x300.png?text=Notebooks', 300);

COMMENT ON TABLE products IS 'Catalog of products available in the store';
COMMENT ON TABLE customer_orders IS 'Orders placed by customers through the store frontend';
COMMENT ON TABLE order_items IS 'Line items for each customer order';
