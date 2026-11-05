from flask import Blueprint, render_template
from models import db, GarbageCategory, SellingTicket, Transaction, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    categories = GarbageCategory.query.filter_by(status='active').all()
    
    # Impact counters
    total_recycled_kg = db.session.query(db.func.sum(Transaction.actual_weight)).scalar() or 1250.0
    total_payouts = db.session.query(db.func.sum(Transaction.total_amount)).scalar() or 48500.0
    total_sellers = User.query.filter_by(role='seller').count() or 150
    total_buyers = User.query.filter_by(role='buyer').count() or 35
    total_tickets = SellingTicket.query.count() or 220

    # Trees saved / carbon offset estimate based on KG collected
    co2_offset_kg = round(float(total_recycled_kg) * 1.8, 1)

    return render_template(
        'index.html',
        categories=categories,
        total_recycled_kg=float(total_recycled_kg),
        total_payouts=float(total_payouts),
        total_sellers=total_sellers,
        total_buyers=total_buyers,
        total_tickets=total_tickets,
        co2_offset_kg=co2_offset_kg
    )

