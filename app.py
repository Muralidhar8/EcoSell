import os
from decimal import Decimal
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash
from config import config_by_name, Config
from models import (
    db, User, SellerProfile, BuyerProfile, GarbageCategory,
    SellingTicket, BuyerPrice, BuyerOffer, Pickup, Transaction, Review, Complaint, Notification
)
from routes import register_blueprints

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please sign in to access this page."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, Config))

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register all application blueprints
    register_blueprints(app)

    # Global template context processor
    @app.context_processor
    def inject_globals():
        unread_count = 0
        user_notifications = []
        if current_user.is_authenticated:
            try:
                unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
                user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
            except Exception:
                pass
        return {
            'app_name': 'EcoSell',
            'app_tagline': 'Smart Waste Management & Recycling Marketplace',
            'unread_notifications_count': unread_count,
            'header_notifications': user_notifications,
            'now': datetime.utcnow()
        }

    # Custom Jinja filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    @app.template_filter('datetime_format')
    def datetime_format_filter(value, format='%b %d, %Y %I:%M %p'):
        if isinstance(value, datetime):
            return value.strftime(format)
        return value

    @app.template_filter('date_format')
    def date_format_filter(value, format='%b %d, %Y'):
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        return value

    # Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

def seed_initial_data(app):
    """Seed categories and demo accounts if database is fresh."""
    with app.app_context():
        try:
            db.create_all()

            # Seed 12 Garbage Categories if empty
            if GarbageCategory.query.count() == 0:
                categories = [
                    GarbageCategory(id=1, category_name='Plastic', description='Plastic bottles, containers, polybags, HDPE, LDPE, PVC and other rigid & flexible plastics.', image='cat_plastic.jpg', status='active'),
                    GarbageCategory(id=2, category_name='Paper', description='Office paper, notebooks, textbooks, envelopes, white and coloured shredded paper.', image='cat_paper.jpg', status='active'),
                    GarbageCategory(id=3, category_name='Newspapers', description='Daily newspapers, magazines, periodicals, circulars and printed newsprint.', image='cat_newspaper.jpg', status='active'),
                    GarbageCategory(id=4, category_name='Cardboard', description='Corrugated packaging boxes, shipping cartons, brown board and egg crates.', image='cat_cardboard.jpg', status='active'),
                    GarbageCategory(id=5, category_name='Iron', description='Scrap iron, cast iron gates, reinforcement bars, metal frames and machinery parts.', image='cat_iron.jpg', status='active'),
                    GarbageCategory(id=6, category_name='Steel', description='Stainless steel kitchen utensils, structural steel, pipes, sheets and sinks.', image='cat_steel.jpg', status='active'),
                    GarbageCategory(id=7, category_name='Aluminium', description='Aluminium beverage cans, window sections, kitchenware, sheets and foil.', image='cat_aluminium.jpg', status='active'),
                    GarbageCategory(id=8, category_name='Copper', description='Copper wiring, motor windings, water pipes, electrical cables and copper utensils.', image='cat_copper.jpg', status='active'),
                    GarbageCategory(id=9, category_name='Glass', description='Glass bottles, condiment jars, glassware and intact or broken container glass.', image='cat_glass.jpg', status='active'),
                    GarbageCategory(id=10, category_name='Electronic Waste', description='Laptops, mobile devices, monitors, circuit boards, cables and defunct home appliances.', image='cat_ewaste.jpg', status='active'),
                    GarbageCategory(id=11, category_name='Old Clothes', description='Used fabrics, wearable clothes, bedsheets, denim, curtains and industrial rags.', image='cat_clothes.jpg', status='active'),
                    GarbageCategory(id=12, category_name='Other Recyclable Materials', description='Rubber tyres, composite recyclables, lead-acid batteries and miscellaneous scrap.', image='cat_other.jpg', status='active'),
                ]
                db.session.bulk_save_objects(categories)
                db.session.commit()
                print("Seeded 12 garbage categories successfully.")

            # Seed Admin if not exists
            admin = User.query.filter_by(email='admin@ecosell.com').first()
            if not admin:
                admin = User(
                    full_name='EcoSell Administrator',
                    email='admin@ecosell.com',
                    phone='+91 9900011223',
                    role='admin',
                    account_status='active'
                )
                admin.set_password('admin123')
                db.session.add(admin)

            # Seed Demo Seller if not exists
            seller = User.query.filter_by(email='seller@ecosell.com').first()
            if not seller:
                seller = User(
                    full_name='Rahul Sharma',
                    email='seller@ecosell.com',
                    phone='+91 9876543210',
                    role='seller',
                    account_status='active'
                )
                seller.set_password('password123')
                db.session.add(seller)
                db.session.flush()

                seller_profile = SellerProfile(
                    user_id=seller.id,
                    address='Flat 402, Green Meadows Apartment, MG Road',
                    city='Mumbai',
                    state='Maharashtra',
                    pincode='400001',
                    latitude=19.0760,
                    longitude=72.8777
                )
                db.session.add(seller_profile)

            # Seed Demo Buyers if not exists
            buyer1 = User.query.filter_by(email='buyer1@ecosell.com').first()
            if not buyer1:
                buyer1 = User(
                    full_name='Amit Patel',
                    email='buyer1@ecosell.com',
                    phone='+91 9876543211',
                    role='buyer',
                    account_status='active'
                )
                buyer1.set_password('password123')
                db.session.add(buyer1)
                db.session.flush()

                buyer1_profile = BuyerProfile(
                    user_id=buyer1.id,
                    shop_name='GreenScrap Traders & Recyclers',
                    shop_address='Plot 12, Industrial Scrap Yard, Andheri East',
                    city='Mumbai',
                    state='Maharashtra',
                    pincode='400069',
                    service_area='Andheri, Bandra, Powai, Kurla',
                    verification_status='verified',
                    rating=4.90
                )
                db.session.add(buyer1_profile)

                # Set buyer1 standard rates
                rates = [
                    (1, 14.00), (2, 15.50), (3, 16.00), (4, 9.50),
                    (5, 32.00), (6, 45.00), (7, 105.00), (8, 520.00), (9, 3.50), (10, 42.00)
                ]
                for cat_id, rate in rates:
                    db.session.add(BuyerPrice(buyer_id=buyer1.id, category_id=cat_id, price_per_kg=rate))

            buyer2 = User.query.filter_by(email='buyer2@ecosell.com').first()
            if not buyer2:
                buyer2 = User(
                    full_name='Priya Verma',
                    email='buyer2@ecosell.com',
                    phone='+91 9876543212',
                    role='buyer',
                    account_status='active'
                )
                buyer2.set_password('password123')
                db.session.add(buyer2)
                db.session.flush()

                buyer2_profile = BuyerProfile(
                    user_id=buyer2.id,
                    shop_name='EcoRecycle Hub Pvt Ltd',
                    shop_address='Shop 7, Gandhi Market, Dadar West',
                    city='Mumbai',
                    state='Maharashtra',
                    pincode='400028',
                    service_area='Dadar, Worli, Parel, Matunga',
                    verification_status='verified',
                    rating=4.85
                )
                db.session.add(buyer2_profile)

            db.session.commit()
            print("Database initialized and demo accounts verified.")
        except Exception as e:
            db.session.rollback()
            print(f"Database initialization notice: {e}")

app = create_app()

if __name__ == '__main__':
    seed_initial_data(app)
    app.run(host='0.0.0.0', port=5000, debug=True)

