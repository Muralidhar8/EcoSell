-- ===================================================
-- Smart Waste Management & Recycling Marketplace (EcoSell)
-- Database Schema (MySQL 8.0+)
-- Database: smart_waste_management
-- ===================================================

CREATE DATABASE IF NOT EXISTS smart_waste_management
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smart_waste_management;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(25) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('seller', 'buyer', 'admin') NOT NULL,
    account_status ENUM('active', 'pending', 'suspended') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Seller Profiles
CREATE TABLE IF NOT EXISTS seller_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(15) NOT NULL,
    latitude DECIMAL(10, 8) NULL,
    longitude DECIMAL(11, 8) NULL,
    CONSTRAINT fk_seller_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Buyer Profiles
CREATE TABLE IF NOT EXISTS buyer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    shop_name VARCHAR(150) NOT NULL,
    shop_address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(15) NOT NULL,
    service_area VARCHAR(255) NOT NULL,
    verification_status ENUM('pending', 'verified', 'rejected') DEFAULT 'pending',
    rating DECIMAL(3, 2) DEFAULT 5.00,
    CONSTRAINT fk_buyer_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_buyer_status (verification_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Garbage Categories
CREATE TABLE IF NOT EXISTS garbage_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    image VARCHAR(255) NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    INDEX idx_category_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Selling Tickets
CREATE TABLE IF NOT EXISTS selling_tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_number VARCHAR(50) NOT NULL UNIQUE,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    estimated_quantity DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(10) DEFAULT 'kg',
    garbage_condition ENUM('Clean', 'Sorted', 'Unsorted') NOT NULL DEFAULT 'Clean',
    description TEXT,
    image VARCHAR(255) NULL,
    pickup_address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    pincode VARCHAR(15) NOT NULL,
    preferred_pickup_date DATE NOT NULL,
    preferred_pickup_time VARCHAR(50) NOT NULL,
    status ENUM('Open', 'Offer Accepted', 'Scheduled', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Open',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_category FOREIGN KEY (category_id) REFERENCES garbage_categories(id) ON DELETE RESTRICT,
    INDEX idx_ticket_status (status),
    INDEX idx_ticket_seller (seller_id),
    INDEX idx_ticket_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Buyer Prices (Catalog rates per kg)
CREATE TABLE IF NOT EXISTS buyer_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    category_id INT NOT NULL,
    price_per_kg DECIMAL(10, 2) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_price_buyer FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_price_category FOREIGN KEY (category_id) REFERENCES garbage_categories(id) ON DELETE CASCADE,
    UNIQUE KEY uq_buyer_category (buyer_id, category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Buyer Offers (Bids on specific tickets)
CREATE TABLE IF NOT EXISTS buyer_offers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    buyer_id INT NOT NULL,
    offered_price_per_kg DECIMAL(10, 2) NOT NULL,
    estimated_total DECIMAL(10, 2) NOT NULL,
    offer_status ENUM('Pending', 'Accepted', 'Rejected', 'Withdrawn', 'Closed') DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_offer_ticket FOREIGN KEY (ticket_id) REFERENCES selling_tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_offer_buyer FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_offer_ticket (ticket_id),
    INDEX idx_offer_buyer (buyer_id),
    INDEX idx_offer_status (offer_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Pickups Table
CREATE TABLE IF NOT EXISTS pickups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    buyer_id INT NOT NULL,
    seller_id INT NOT NULL,
    pickup_date DATE NOT NULL,
    pickup_time VARCHAR(50) NOT NULL,
    actual_weight DECIMAL(10, 2) NULL,
    pickup_status ENUM('Pending', 'Scheduled', 'Buyer On The Way', 'Arrived', 'Garbage Collected', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    collection_notes TEXT NULL,
    completed_at DATETIME NULL,
    CONSTRAINT fk_pickup_ticket FOREIGN KEY (ticket_id) REFERENCES selling_tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_pickup_buyer FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_pickup_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_pickup_buyer (buyer_id),
    INDEX idx_pickup_seller (seller_id),
    INDEX idx_pickup_status (pickup_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    buyer_id INT NOT NULL,
    seller_id INT NOT NULL,
    actual_weight DECIMAL(10, 2) NOT NULL,
    price_per_kg DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('Cash', 'UPI', 'Online') NOT NULL DEFAULT 'Cash',
    payment_status ENUM('Pending', 'Completed', 'Failed') DEFAULT 'Completed',
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_trans_ticket FOREIGN KEY (ticket_id) REFERENCES selling_tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_trans_buyer FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_trans_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_trans_buyer (buyer_id),
    INDEX idx_trans_seller (seller_id),
    INDEX idx_trans_date (transaction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    seller_id INT NOT NULL,
    buyer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_review_ticket FOREIGN KEY (ticket_id) REFERENCES selling_tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_review_buyer FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_review_buyer (buyer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ticket_id INT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    complaint_status ENUM('Open', 'Under Review', 'Resolved', 'Closed') DEFAULT 'Open',
    admin_response TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_complaint_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_complaint_ticket FOREIGN KEY (ticket_id) REFERENCES selling_tickets(id) ON DELETE SET NULL,
    INDEX idx_complaint_user (user_id),
    INDEX idx_complaint_status (complaint_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

