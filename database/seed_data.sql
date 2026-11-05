-- ===================================================
-- Smart Waste Management & Recycling Marketplace (EcoSell)
-- Seed Data Script
-- Database: smart_waste_management
-- ===================================================

USE smart_waste_management;

-- 1. Insert Predefined Garbage Categories
INSERT INTO garbage_categories (id, category_name, description, image, status) VALUES
(1, 'Plastic', 'Plastic bottles, containers, polybags, HDPE, LDPE, PVC and other rigid & flexible plastics.', 'cat_plastic.jpg', 'active'),
(2, 'Paper', 'Office paper, notebooks, textbooks, envelopes, white and coloured shredded paper.', 'cat_paper.jpg', 'active'),
(3, 'Newspapers', 'Daily newspapers, magazines, periodicals, circulars and printed newsprint.', 'cat_newspaper.jpg', 'active'),
(4, 'Cardboard', 'Corrugated packaging boxes, shipping cartons, brown board and egg crates.', 'cat_cardboard.jpg', 'active'),
(5, 'Iron', 'Scrap iron, cast iron gates, reinforcement bars, metal frames and machinery parts.', 'cat_iron.jpg', 'active'),
(6, 'Steel', 'Stainless steel kitchen utensils, structural steel, pipes, sheets and sinks.', 'cat_steel.jpg', 'active'),
(7, 'Aluminium', 'Aluminium beverage cans, window sections, kitchenware, sheets and foil.', 'cat_aluminium.jpg', 'active'),
(8, 'Copper', 'Copper wiring, motor windings, water pipes, electrical cables and copper utensils.', 'cat_copper.jpg', 'active'),
(9, 'Glass', 'Glass bottles, condiment jars, glassware and intact or broken container glass.', 'cat_glass.jpg', 'active'),
(10, 'Electronic Waste', 'Laptops, mobile devices, monitors, circuit boards, cables and defunct home appliances.', 'cat_ewaste.jpg', 'active'),
(11, 'Old Clothes', 'Used fabrics, wearable clothes, bedsheets, denim, curtains and industrial rags.', 'cat_clothes.jpg', 'active'),
(12, 'Other Recyclable Materials', 'Rubber tyres, composite recyclables, lead-acid batteries and miscellaneous recyclable scrap.', 'cat_other.jpg', 'active')
ON DUPLICATE KEY UPDATE category_name=VALUES(category_name);

-- 2. Insert Demo Users (Passwords: admin123 for admin, password123 for others)
-- User 1: Admin
-- User 2: Seller (Rahul Sharma)
-- User 3: Buyer 1 (Amit Patel - GreenScrap Traders)
-- User 4: Buyer 2 (Priya Verma - EcoRecycle Hub)
-- User 5: Buyer 3 (Rajesh Kumar - Metro Metal & Scrap)
INSERT INTO users (id, full_name, email, phone, password_hash, role, account_status, created_at) VALUES
(1, 'EcoSell Administrator', 'admin@ecosell.com', '+91 9900011223', 'scrypt:32768:8:1$ZVaoEmG6ohVCDgNR$649b12c23ffb222866b1e9be75e5f428289039c6a559c34bcc3c507bd7a9d81e22719f78b31b57a6a1a8702939b6569e66b876bcba8b2acd9eb54136f8b1c865', 'admin', 'active', NOW()),
(2, 'Rahul Sharma', 'seller@ecosell.com', '+91 9876543210', 'scrypt:32768:8:1$MeGmrSIQeL13QZlM$fc9a515f3f1b7604aaebcef93be5c0bce92e30892f181b2763dd2c167f5fcfe855db2a84caa2e6dca5fa878a6aabada156d23e29dfa290d03b0c911f83bc35ef', 'seller', 'active', NOW()),
(3, 'Amit Patel', 'buyer1@ecosell.com', '+91 9876543211', 'scrypt:32768:8:1$MeGmrSIQeL13QZlM$fc9a515f3f1b7604aaebcef93be5c0bce92e30892f181b2763dd2c167f5fcfe855db2a84caa2e6dca5fa878a6aabada156d23e29dfa290d03b0c911f83bc35ef', 'buyer', 'active', NOW()),
(4, 'Priya Verma', 'buyer2@ecosell.com', '+91 9876543212', 'scrypt:32768:8:1$MeGmrSIQeL13QZlM$fc9a515f3f1b7604aaebcef93be5c0bce92e30892f181b2763dd2c167f5fcfe855db2a84caa2e6dca5fa878a6aabada156d23e29dfa290d03b0c911f83bc35ef', 'buyer', 'active', NOW()),
(5, 'Rajesh Kumar', 'buyer3@ecosell.com', '+91 9876543213', 'scrypt:32768:8:1$MeGmrSIQeL13QZlM$fc9a515f3f1b7604aaebcef93be5c0bce92e30892f181b2763dd2c167f5fcfe855db2a84caa2e6dca5fa878a6aabada156d23e29dfa290d03b0c911f83bc35ef', 'buyer', 'active', NOW())
ON DUPLICATE KEY UPDATE email=VALUES(email);

-- 3. Insert Seller Profile
INSERT INTO seller_profiles (id, user_id, address, city, state, pincode, latitude, longitude) VALUES
(1, 2, 'Flat 402, Green Meadows Apartment, MG Road', 'Mumbai', 'Maharashtra', '400001', 19.07600000, 72.87770000)
ON DUPLICATE KEY UPDATE address=VALUES(address);

-- 4. Insert Buyer Profiles
INSERT INTO buyer_profiles (id, user_id, shop_name, shop_address, city, state, pincode, service_area, verification_status, rating) VALUES
(1, 3, 'GreenScrap Traders & Recyclers', 'Plot 12, Industrial Scrap Yard, Andheri East', 'Mumbai', 'Maharashtra', '400069', 'Andheri, Bandra, Powai, Kurla', 'verified', 4.90),
(2, 4, 'EcoRecycle Hub Pvt Ltd', 'Shop 7, Gandhi Market, Dadar West', 'Mumbai', 'Maharashtra', '400028', 'Dadar, Worli, Parel, Matunga', 'verified', 4.85),
(3, 5, 'Metro Metal & Scrap Store', 'Shed 4B, Kurla Scrap Market, Kurla West', 'Mumbai', 'Maharashtra', '400070', 'Kurla, Chembur, Ghatkopar', 'pending', 4.70)
ON DUPLICATE KEY UPDATE shop_name=VALUES(shop_name);

-- 5. Insert Buyer Prices
INSERT INTO buyer_prices (buyer_id, category_id, price_per_kg) VALUES
-- Buyer 1 (Amit Patel) Rates
(3, 1, 14.00), -- Plastic
(3, 2, 15.50), -- Paper
(3, 3, 16.00), -- Newspapers
(3, 4, 9.50),  -- Cardboard
(3, 5, 32.00), -- Iron
(3, 6, 45.00), -- Steel
(3, 7, 105.00),-- Aluminium
(3, 8, 520.00),-- Copper
(3, 9, 3.50),  -- Glass
(3, 10, 42.00),-- E-Waste
-- Buyer 2 (Priya Verma) Rates
(4, 1, 13.50),
(4, 2, 14.50),
(4, 3, 15.00),
(4, 4, 10.00),
(4, 5, 30.00),
(4, 6, 42.00),
(4, 7, 110.00),
(4, 8, 510.00),
(4, 10, 45.00)
ON DUPLICATE KEY UPDATE price_per_kg=VALUES(price_per_kg);

-- 6. Insert Sample Selling Tickets
INSERT INTO selling_tickets (id, ticket_number, seller_id, category_id, estimated_quantity, unit, garbage_condition, description, image, pickup_address, city, pincode, preferred_pickup_date, preferred_pickup_time, status, created_at) VALUES
(1, 'GARB-2026-0001', 2, 3, 25.00, 'kg', 'Clean', 'Old English and Marathi newspapers bundled neatly with twine. Stored dry indoors.', 'ticket_newspapers.jpg', 'Flat 402, Green Meadows Apartment, MG Road', 'Mumbai', '400001', CURDATE() + INTERVAL 2 DAY, '10:00 AM - 12:00 PM', 'Open', NOW() - INTERVAL 1 DAY),
(2, 'GARB-2026-0002', 2, 4, 40.00, 'kg', 'Sorted', 'Flatted corrugated packaging boxes from online shopping and appliances.', 'ticket_cardboard.jpg', 'Flat 402, Green Meadows Apartment, MG Road', 'Mumbai', '400001', CURDATE() + INTERVAL 3 DAY, '02:00 PM - 04:00 PM', 'Open', NOW() - INTERVAL 12 HOUR),
(3, 'GARB-2026-0003', 2, 8, 8.50, 'kg', 'Clean', 'Copper pipes and electrical motor wire scraps collected from home renovation.', 'ticket_copper.jpg', 'Flat 402, Green Meadows Apartment, MG Road', 'Mumbai', '400001', CURDATE() - INTERVAL 2 DAY, '11:00 AM - 01:00 PM', 'Completed', NOW() - INTERVAL 5 DAY)
ON DUPLICATE KEY UPDATE ticket_number=VALUES(ticket_number);

-- 7. Insert Buyer Offers
INSERT INTO buyer_offers (id, ticket_id, buyer_id, offered_price_per_kg, estimated_total, offer_status, created_at) VALUES
-- Offers on Ticket 1 (Newspapers 25kg)
(1, 1, 3, 16.00, 400.00, 'Pending', NOW() - INTERVAL 20 HOUR),
(2, 1, 4, 15.50, 387.50, 'Pending', NOW() - INTERVAL 18 HOUR),
-- Offer on Ticket 2 (Cardboard 40kg)
(3, 2, 4, 10.00, 400.00, 'Pending', NOW() - INTERVAL 6 HOUR),
-- Completed Offer on Ticket 3 (Copper 8.5kg)
(4, 3, 3, 520.00, 4420.00, 'Accepted', NOW() - INTERVAL 4 DAY)
ON DUPLICATE KEY UPDATE id=VALUES(id);

-- 8. Insert Completed Pickup for Ticket 3
INSERT INTO pickups (id, ticket_id, buyer_id, seller_id, pickup_date, pickup_time, actual_weight, pickup_status, collection_notes, completed_at) VALUES
(1, 3, 3, 2, CURDATE() - INTERVAL 2 DAY, '11:00 AM - 01:00 PM', 8.20, 'Completed', 'Digital scale verification done in presence of seller. Pristine copper grade.', NOW() - INTERVAL 2 DAY)
ON DUPLICATE KEY UPDATE id=VALUES(id);

-- 9. Insert Transaction for Ticket 3 (8.2 kg * Rs 520 = Rs 4264.00)
INSERT INTO transactions (id, ticket_id, buyer_id, seller_id, actual_weight, price_per_kg, total_amount, payment_method, payment_status, transaction_date) VALUES
(1, 3, 3, 2, 8.20, 520.00, 4264.00, 'UPI', 'Completed', NOW() - INTERVAL 2 DAY)
ON DUPLICATE KEY UPDATE id=VALUES(id);

-- 10. Insert Review for Ticket 3
INSERT INTO reviews (id, ticket_id, seller_id, buyer_id, rating, review_text, created_at) VALUES
(1, 3, 2, 3, 5, 'Very courteous scrap dealer! Arrived exactly on scheduled time, weighed on an accurate digital scale, and paid instantly via UPI.', NOW() - INTERVAL 2 DAY)
ON DUPLICATE KEY UPDATE id=VALUES(id);

-- 11. Insert Sample Complaint
INSERT INTO complaints (id, user_id, ticket_id, subject, description, complaint_status, admin_response, created_at) VALUES
(1, 2, NULL, 'Query regarding hazardous battery disposal guidelines', 'Can we list old car lead-acid batteries under Other Recyclable Materials, or is special licensing required?', 'Resolved', 'Lead-acid batteries can be listed under Other Recyclable Materials. Only state-authorized recycling buyers can accept and transport them.', NOW() - INTERVAL 3 DAY)
ON DUPLICATE KEY UPDATE id=VALUES(id);

-- 12. Insert Sample Notifications
INSERT INTO notifications (id, user_id, title, message, is_read, created_at) VALUES
(1, 2, 'Welcome to EcoSell!', 'Your seller account has been activated. Start turning your household and commercial waste into wealth!', 1, NOW() - INTERVAL 5 DAY),
(2, 2, 'New Price Offer Received', 'GreenScrap Traders offered ₹16.00/kg for your ticket GARB-2026-0001 (Newspapers).', 0, NOW() - INTERVAL 20 HOUR),
(3, 2, 'New Price Offer Received', 'EcoRecycle Hub offered ₹15.50/kg for your ticket GARB-2026-0001 (Newspapers).', 0, NOW() - INTERVAL 18 HOUR),
(4, 3, 'Offer Accepted!', 'Seller Rahul Sharma accepted your offer on ticket GARB-2026-0003.', 1, NOW() - INTERVAL 4 DAY),
(5, 2, 'Payment Received ₹4,264.00', 'Transaction complete for ticket GARB-2026-0003 via UPI.', 1, NOW() - INTERVAL 2 DAY)
ON DUPLICATE KEY UPDATE id=VALUES(id);

