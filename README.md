# EcoSell - Smart Waste Management & Recycling Marketplace

EcoSell is a modern, responsive, full-stack web marketplace built with **Python (Flask)**, **MySQL**, **HTML5**, **CSS3**, **JavaScript**, **Bootstrap 5**, and **Chart.js**.

The platform connects households, apartment complexes, offices, and institutions who want to sell recyclable garbage with verified shopkeepers, scrap dealers, and recycling facilities who want to purchase recyclable materials.

---

## 🌟 Key Features

### 1. Seller Module (Households / Waste Generators)
* **Authentication & Profiles:** Seller registration, secure session authentication, and address management.
* **Garbage Ticket Creation:** Professional form with category picker, estimated weight (in kg), condition classification (`Clean`, `Sorted`, `Unsorted`), photo upload, and preferred pickup date/time slot. Automatically assigns unique IDs like `GARB-2026-0001`.
* **Competitive Bid Comparison:** Compare incoming price offers from verified local buyers side-by-side (Rate per kg, Estimated Total, Buyer Rating).
* **Safe Offer Acceptance:** 1-click offer acceptance with database transaction locks that automatically close competing bids and create a scheduled doorstep collection.
* **Live Pickup Tracker:** Visual progress step tracker (`Scheduled` → `On The Way` → `Arrived` → `Weighed` → `Completed`).
* **Earnings & Digital Receipts:** Permanent financial ledgers showing verified actual weights, rates, and payment methods (Cash, UPI, Online).
* **Ratings & Dispute Resolution:** Rate scrap dealers (1–5 stars) and submit complaints directly to the platform admin.

### 2. Buyer Module (Scrap Dealers / Kabadiwalas / Recyclers)
* **Shop Registration & Verification:** Shop name, physical yard address, contact info, and covered service areas (subject to admin verification).
* **Scrap Discovery:** Search and multi-criteria filters for open tickets by category, city/locality, and weight ranges.
* **Benchmark Rate Management:** Set standard purchasing rates per kilogram across all 12 material categories.
* **Competitive Bidding:** Place custom rates per kilogram on specific tickets with real-time dynamic total calculation.
* **Fulfillment & Weigh-In:** Update transit status and record physical scale readings upon arrival.
* **Instant Calculation:** Automatic calculation of final payout: `Final Amount = Verified Actual Weight × Accepted Rate/KG`.
* **Purchase Ledgers:** Comprehensive history of all acquired materials and settled payments.

### 3. Admin Module (Platform Governance & Ecology Analytics)
* **Operations Dashboard:** Real-time metrics for registered users, tickets, collected scrap volume (kg), and financial turnover.
* **Interactive Chart.js Visualizations:** Monthly recycling trends and material stream distribution charts.
* **Scrap Dealer Verification:** Review pending dealer accounts, inspect service areas, and verify or reject.
* **User Control Center:** Search, monitor, and suspend/activate seller and buyer accounts.
* **Category Management:** Manage the 12 predefined categories or add new custom recyclable streams.
* **Ticket & Transaction Audit:** Full transparency across all platform tickets, bids, and payment records.
* **Complaint Mediation:** Investigate seller/buyer disputes and provide official administrative resolutions.
* **Environmental Impact Reports:** Exportable reports calculating landfill diversion and carbon emissions offset ($1.8\text{ kg CO}_2\text{e}$ per kg recycled).

---

## 📦 Supported Garbage Categories

EcoSell includes 12 predefined categories:
1. **Plastic** (PET bottles, HDPE, LDPE, PVC containers)
2. **Paper** (Office paper, books, notebooks, shredded paper)
3. **Newspapers** (Daily newsprint, periodicals, magazines)
4. **Cardboard** (Corrugated shipping boxes, packaging board)
5. **Iron** (Scrap iron, cast iron gates, rebars, machinery parts)
6. **Steel** (Stainless steel utensils, structural steel, pipes)
7. **Aluminium** (Beverage cans, window frames, sheets, kitchenware)
8. **Copper** (Electrical wiring, motor winding, pipes, cables)
9. **Glass** (Bottles, jars, container glass)
10. **Electronic Waste** (Computer parts, phones, batteries, appliances)
11. **Old Clothes** (Textiles, wearable fabrics, denim, linens)
12. **Other Recyclable Materials** (Rubber tyres, lead-acid batteries, composite scrap)

---

## 🛠️ Technology Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js, Leaflet.js
* **Backend:** Python 3.12+, Flask 3.1+, Flask-Login, Flask-SQLAlchemy, Werkzeug, python-dotenv
* **Database:** MySQL 8.0+ / PyMySQL (with transparent SQLite fallback for memory/testing environments)
* **Architecture:** Modular MVC / Application Factory with blueprints (`auth`, `seller`, `buyer`, `admin`, `main`), database models, and service layer.

---

## 📂 Project Structure

```
d:\New Project\
├── app.py                      # Application factory and bootstrap initialization
├── config.py                   # Environment configuration & DB connection parameters
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment variables
├── README.md                   # Documentation and execution guide
├── database/
│   ├── schema.sql              # MySQL DDL schema script
│   └── seed_data.sql           # MySQL sample data & demo users script
├── models/
│   ├── __init__.py             # SQLAlchemy DB instance and model exports
│   ├── user.py                 # User model (UserMixin, roles, password hashing)
│   ├── seller.py               # SellerProfile model
│   ├── buyer.py                # BuyerProfile model
│   ├── category.py             # GarbageCategory model
│   ├── ticket.py               # SellingTicket model (GARB-YYYY-XXXX generator)
│   ├── offer.py                # BuyerOffer & BuyerPrice models
│   ├── pickup.py               # Pickup tracking model
│   ├── transaction.py          # Permanent transaction ledger model
│   ├── review.py               # Reviews & ratings model
│   ├── complaint.py            # User grievances and admin resolution model
│   └── notification.py         # Notifications model
├── routes/
│   ├── __init__.py             # Blueprint registration
│   ├── decorators.py           # Role-based decorators (@seller_required, @buyer_required, @admin_required)
│   ├── main_routes.py          # Public landing page with impact counters
│   ├── auth_routes.py          # Registration, login, logout, notifications AJAX
│   ├── seller_routes.py        # Seller dashboard, ticket creation, offers, pickups, earnings
│   ├── buyer_routes.py         # Buyer dashboard, browse, bidding, rates, collection weigh-in
│   └── admin_routes.py         # Admin control panel, verification, complaints, reports
├── services/
│   ├── __init__.py
│   ├── ticket_service.py       # Ticket numbering and creation logic
│   ├── offer_service.py        # Safe offer submission & concurrent acceptance transactions
│   ├── payment_service.py      # Actual weighing, calculation & payment completion logic
│   └── notification_service.py # User notifications engine
├── templates/
│   ├── base.html               # Master layout with navbar, footer, modals
│   ├── dashboard_base.html     # Dedicated dashboard shell with sidebar & topbar
│   ├── index.html              # Modern commercial landing page
│   ├── auth/                   # Login, register seller, register buyer
│   ├── seller/                 # Seller portal templates
│   ├── buyer/                  # Buyer portal templates
│   ├── admin/                  # Admin portal templates
│   └── errors/                 # 403, 404, 500 error pages
├── static/
│   ├── css/style.css           # EcoSell custom green & white theme stylesheet
│   ├── js/main.js              # Client-side calculations, notifications, image preview
│   └── uploads/                # Secure local storage for ticket photos
└── tests/
    ├── __init__.py
    └── test_workflow.py        # Comprehensive end-to-end integration test suite
```

---

## 🚀 Installation & Setup Guide (Windows / VS Code)

### 1. Prerequisites
* **Python 3.10+** installed and added to your `PATH`.
* **MySQL Server 8.0+** and **MySQL Workbench** installed (or any MySQL instance).

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the root folder:
```powershell
Copy-Item .env.example .env
```
Update your MySQL credentials in `.env`:
```ini
FLASK_ENV=development
SECRET_KEY=ecosell-super-secret-key-2026

# MySQL Credentials
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=smart_waste_management
```

### 3. Initialize MySQL Database
Open **MySQL Workbench** or your MySQL command line client and execute:
```sql
SOURCE database/schema.sql;
SOURCE database/seed_data.sql;
```
*(Alternatively, when running `python app.py`, the application will automatically create all tables and seed categories and demo accounts if they are not yet populated!)*

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Run the Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🔑 Demo Login Accounts

| Role | Email | Password | Access / Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@ecosell.com` | `admin123` | Full dashboard, verify scrap dealers, manage categories, resolve complaints |
| **Seller** | `seller@ecosell.com` | `password123` | Create tickets, upload photos, compare bids, accept offers, track payouts |
| **Buyer 1** | `buyer1@ecosell.com` | `password123` | *GreenScrap Traders* (Verified): Browse tickets, submit bids, weigh & pay |
| **Buyer 2** | `buyer2@ecosell.com` | `password123` | *EcoRecycle Hub* (Verified): Competing scrap dealer |
| **Buyer 3** | `buyer3@ecosell.com` | `password123` | *Metro Metal Store* (Pending verification demo) |

---

## 🧪 Running Automated Tests

Run the full end-to-end workflow test suite with:
```powershell
python tests/test_workflow.py
```
This executes automated testing covering:
1. Public landing page rendering and category catalog.
2. Seller registration and profile creation.
3. Buyer registration with pending verification status.
4. Complete end-to-end marketplace scenario:
   * Seller creates ticket `GARB-YYYY-XXXX` for 30 kg of sorted plastic.
   * Buyer 1 submits price bid @ ₹15.00/kg.
   * Buyer 2 submits competing bid @ ₹16.50/kg.
   * Seller accepts Buyer 2's offer; system automatically rejects competing bids and schedules doorstep pickup.
   * Buyer arrives, verifies weight on digital scale (32.5 kg).
   * System calculates final payment: $32.5\text{ kg} \times ₹16.50 = ₹536.25$.
   * Records payment via UPI, marks transaction complete, and seller posts review.

---

## 📜 Business Rules Enforced
1. **Concurrency Protection:** Sellers can accept only one offer per ticket; database transactions safely mark all competing offers closed and prevent duplicate acceptance.
2. **Self-Bidding Prevention:** Buyers cannot place bids on their own tickets.
3. **Weight-Based Payouts:** Final payment is strictly computed from verified actual scale weight, not initial estimated weight.
4. **Verification Safeguards:** Only verified scrap dealers can place active price bids and collect recyclable materials.

