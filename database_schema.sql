-- Rice Mill Management System Database Schema
-- Enhanced version with additional tables and improvements

-- Brokers table (unchanged)
CREATE TABLE brokers (
    broker_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    commission_rate DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Customers table (enhanced)
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    broker_id INT,
    credit_limit DECIMAL(10,2) DEFAULT 0.00,
    current_balance DECIMAL(10,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (broker_id) REFERENCES brokers(broker_id) ON DELETE SET NULL
);

-- Rice types table (enhanced)
CREATE TABLE rice_types (
    rice_type_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    standard_price DECIMAL(10,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Paddy types table (enhanced)
CREATE TABLE paddy_types (
    paddy_type_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    standard_price DECIMAL(10,2) DEFAULT 0.00,
    yield_percentage DECIMAL(5,2) DEFAULT 0.00, -- Expected rice yield from paddy
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers table (new)
CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    contact_person VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Warehouses/Locations table (new)
CREATE TABLE warehouses (
    warehouse_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    capacity_bags INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced purchases table
CREATE TABLE purchases (
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_id INT,
    paddy_type_id INT,
    no_of_bags INT NOT NULL,
    price_per_bag DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    warehouse_id INT,
    purchase_date DATE NOT NULL,
    delivery_date DATE,
    payment_status ENUM('pending', 'partial', 'paid') DEFAULT 'pending',
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    quality_grade ENUM('A', 'B', 'C') DEFAULT 'B',
    moisture_content DECIMAL(5,2), -- Percentage
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    FOREIGN KEY (paddy_type_id) REFERENCES paddy_types(paddy_type_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE SET NULL
);

-- Milling operations table (new)
CREATE TABLE milling_operations (
    operation_id INT PRIMARY KEY AUTO_INCREMENT,
    purchase_id INT,
    paddy_type_id INT,
    input_bags INT NOT NULL,
    output_rice_type_id INT,
    output_bags INT NOT NULL,
    milling_date DATE NOT NULL,
    milling_cost DECIMAL(10,2) DEFAULT 0.00,
    wastage_percentage DECIMAL(5,2) DEFAULT 0.00,
    operator_name VARCHAR(100),
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE SET NULL,
    FOREIGN KEY (paddy_type_id) REFERENCES paddy_types(paddy_type_id),
    FOREIGN KEY (output_rice_type_id) REFERENCES rice_types(rice_type_id)
);

-- Enhanced sales table
CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    broker_id INT,
    rice_type_id INT,
    no_of_bags INT NOT NULL,
    price_per_bag DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    sold_date DATE NOT NULL,
    delivery_date DATE,
    payment_status ENUM('pending', 'partial', 'paid') DEFAULT 'pending',
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    cd_amount DECIMAL(10,2) DEFAULT 0.00, -- Cash discount
    broker_commission DECIMAL(10,2) DEFAULT 0.00,
    delivery_address TEXT,
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (broker_id) REFERENCES brokers(broker_id) ON DELETE SET NULL,
    FOREIGN KEY (rice_type_id) REFERENCES rice_types(rice_type_id)
);

-- Enhanced rice stock table
CREATE TABLE rice_stock (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    rice_type_id INT,
    warehouse_id INT,
    total_bags INT DEFAULT 0,
    reserved_bags INT DEFAULT 0, -- Bags reserved for pending orders
    available_bags INT DEFAULT 0, -- total_bags - reserved_bags
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rice_type_id) REFERENCES rice_types(rice_type_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE SET NULL,
    UNIQUE KEY unique_stock (rice_type_id, warehouse_id)
);

-- Paddy stock table (new)
CREATE TABLE paddy_stock (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    paddy_type_id INT,
    warehouse_id INT,
    total_bags INT DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (paddy_type_id) REFERENCES paddy_types(paddy_type_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE SET NULL,
    UNIQUE KEY unique_paddy_stock (paddy_type_id, warehouse_id)
);

-- Enhanced payments table
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_type ENUM('purchase', 'sale', 'misc', 'broker_commission') NOT NULL,
    related_id INT, -- ID of the related sale/purchase
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    paid_to VARCHAR(100),
    paid_by VARCHAR(100),
    payment_mode ENUM('cash', 'cheque', 'bank_transfer', 'upi') DEFAULT 'cash',
    cheque_number VARCHAR(50),
    bank_name VARCHAR(100),
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Expenses table (new)
CREATE TABLE expenses (
    expense_id INT PRIMARY KEY AUTO_INCREMENT,
    expense_category ENUM('milling', 'transport', 'electricity', 'maintenance', 'salary', 'other') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    expense_date DATE NOT NULL,
    description TEXT,
    paid_to VARCHAR(100),
    payment_mode ENUM('cash', 'cheque', 'bank_transfer') DEFAULT 'cash',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Users table for system access (new)
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role ENUM('admin', 'manager', 'operator') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Audit log table (new)
CREATE TABLE audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Indexes for better performance
CREATE INDEX idx_customers_broker ON customers(broker_id);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_broker ON sales(broker_id);
CREATE INDEX idx_sales_date ON sales(sold_date);
CREATE INDEX idx_purchases_supplier ON purchases(supplier_id);
CREATE INDEX idx_purchases_date ON purchases(purchase_date);
CREATE INDEX idx_payments_type ON payments(payment_type);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_table ON audit_log(table_name);

-- Insert default data
INSERT INTO warehouses (name, address, capacity_bags) VALUES 
('Main Warehouse', 'Main facility location', 10000),
('Secondary Warehouse', 'Secondary storage location', 5000);

INSERT INTO users (username, password_hash, full_name, role) VALUES 
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'System Administrator', 'admin');

-- Sample rice types
INSERT INTO rice_types (name, description, standard_price) VALUES 
('Basmati Rice', 'Premium long grain rice', 120.00),
('Sona Masoori', 'Medium grain rice', 80.00),
('Ponni Rice', 'Short grain rice', 75.00),
('Raw Rice', 'Unpolished rice', 70.00);

-- Sample paddy types
INSERT INTO paddy_types (name, description, standard_price, yield_percentage) VALUES 
('Basmati Paddy', 'Premium basmati paddy', 60.00, 65.00),
('Sona Masoori Paddy', 'Medium grain paddy', 45.00, 68.00),
('Ponni Paddy', 'Short grain paddy', 42.00, 70.00); 