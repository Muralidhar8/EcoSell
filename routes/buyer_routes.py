from decimal import Decimal
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models import (
    db, User, BuyerProfile, GarbageCategory, SellingTicket,
    BuyerPrice, BuyerOffer, Pickup, Transaction, Review
)
from services.offer_service import OfferService
from services.payment_service import PaymentService
from routes.decorators import buyer_required

buyer_bp = Blueprint('buyer', __name__, url_prefix='/buyer')

@buyer_bp.route('/dashboard')
@login_required
@buyer_required
def dashboard():
    buyer_id = current_user.id
    profile = current_user.buyer_profile

    # Dynamic metrics from database
    available_tickets = SellingTicket.query.filter_by(status='Open').count()
    offers_submitted = BuyerOffer.query.filter_by(buyer_id=buyer_id).count()
    accepted_offers = BuyerOffer.query.filter_by(buyer_id=buyer_id, offer_status='Accepted').count()
    scheduled_pickups = Pickup.query.filter(
        Pickup.buyer_id == buyer_id,
        Pickup.pickup_status.in_(['Scheduled', 'Buyer On The Way', 'Arrived', 'Garbage Collected'])
    ).count()

    # Total purchases
    total_purchased_kg_query = db.session.query(db.func.sum(Transaction.actual_weight)).filter(
        Transaction.buyer_id == buyer_id,
        Transaction.payment_status == 'Completed'
    ).scalar()
    total_purchased_kg = float(total_purchased_kg_query or 0.0)

    total_spent_query = db.session.query(db.func.sum(Transaction.total_amount)).filter(
        Transaction.buyer_id == buyer_id,
        Transaction.payment_status == 'Completed'
    ).scalar()
    total_spent = float(total_spent_query or 0.0)

    # Category breakdown for Chart.js
    category_stats = db.session.query(
        GarbageCategory.category_name,
        db.func.sum(Transaction.actual_weight)
    ).join(SellingTicket, SellingTicket.category_id == GarbageCategory.id)\
     .join(Transaction, Transaction.ticket_id == SellingTicket.id)\
     .filter(Transaction.buyer_id == buyer_id, Transaction.payment_status == 'Completed')\
     .group_by(GarbageCategory.category_name).all()

    cat_labels = [c[0] for c in category_stats] if category_stats else ['No purchases yet']
    cat_values = [float(c[1]) for c in category_stats] if category_stats else [0]

    # Recent available tickets
    recent_available = SellingTicket.query.filter_by(status='Open').order_by(
        SellingTicket.created_at.desc()
    ).limit(5).all()

    # Active upcoming pickups
    active_pickups = Pickup.query.filter(
        Pickup.buyer_id == buyer_id,
        Pickup.pickup_status != 'Completed',
        Pickup.pickup_status != 'Cancelled'
    ).order_by(Pickup.pickup_date.asc()).limit(5).all()

    return render_template(
        'buyer/dashboard.html',
        profile=profile,
        available_tickets=available_tickets,
        offers_submitted=offers_submitted,
        accepted_offers=accepted_offers,
        scheduled_pickups=scheduled_pickups,
        total_purchased_kg=total_purchased_kg,
        total_spent=total_spent,
        recent_available=recent_available,
        active_pickups=active_pickups,
        cat_labels=cat_labels,
        cat_values=cat_values
    )

@buyer_bp.route('/browse')
@login_required
@buyer_required
def browse():
    categories = GarbageCategory.query.filter_by(status='active').order_by(GarbageCategory.category_name).all()
    
    # Filters
    category_id = request.args.get('category_id', type=int)
    city = request.args.get('city', '').strip()
    min_qty = request.args.get('min_qty', type=float)
    max_qty = request.args.get('max_qty', type=float)
    search = request.args.get('q', '').strip()

    query = SellingTicket.query.filter_by(status='Open')

    # Prevent buyer from seeing their own tickets if they also sold something
    query = query.filter(SellingTicket.seller_id != current_user.id)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if city:
        query = query.filter(SellingTicket.city.ilike(f"%{city}%"))
    if min_qty is not None:
        query = query.filter(SellingTicket.estimated_quantity >= min_qty)
    if max_qty is not None:
        query = query.filter(SellingTicket.estimated_quantity <= max_qty)
    if search:
        query = query.filter(
            (SellingTicket.ticket_number.ilike(f"%{search}%")) |
            (SellingTicket.description.ilike(f"%{search}%")) |
            (SellingTicket.pickup_address.ilike(f"%{search}%"))
        )

    tickets = query.order_by(SellingTicket.created_at.desc()).all()

    # Get buyer default price map for quick reference
    buyer_prices = {bp.category_id: float(bp.price_per_kg) for bp in current_user.buyer_prices}

    # Get map of offers this buyer already made on these tickets
    my_offers_map = {
        offer.ticket_id: offer
        for offer in BuyerOffer.query.filter(
            BuyerOffer.buyer_id == current_user.id,
            BuyerOffer.ticket_id.in_([t.id for t in tickets]) if tickets else False
        ).all()
    }

    return render_template(
        'buyer/browse.html',
        tickets=tickets,
        categories=categories,
        buyer_prices=buyer_prices,
        my_offers_map=my_offers_map,
        selected_category=category_id,
        selected_city=city,
        min_qty=min_qty,
        max_qty=max_qty,
        search_query=search
    )

@buyer_bp.route('/tickets/<int:ticket_id>')
@login_required
@buyer_required
def ticket_detail(ticket_id):
    ticket = SellingTicket.query.get_or_404(ticket_id)
    my_offer = BuyerOffer.query.filter_by(ticket_id=ticket.id, buyer_id=current_user.id).first()
    
    # Get standard rate for this category if set by buyer
    standard_price = BuyerPrice.query.filter_by(buyer_id=current_user.id, category_id=ticket.category_id).first()
    suggested_rate = float(standard_price.price_per_kg) if standard_price else 0.0

    # Count total competitors who offered
    competing_offers_count = BuyerOffer.query.filter_by(ticket_id=ticket.id).count()

    pickup = Pickup.query.filter_by(ticket_id=ticket.id).first()
    transaction = Transaction.query.filter_by(ticket_id=ticket.id).first()

    return render_template(
        'buyer/ticket_detail.html',
        ticket=ticket,
        my_offer=my_offer,
        suggested_rate=suggested_rate,
        competing_offers_count=competing_offers_count,
        pickup=pickup,
        transaction=transaction
    )

@buyer_bp.route('/tickets/<int:ticket_id>/offer', methods=['POST'])
@login_required
@buyer_required
def submit_offer(ticket_id):
    if not current_user.is_verified_buyer:
        flash("Your account must be verified by Admin before you can submit price offers to sellers.", "warning")
        return redirect(url_for('buyer.ticket_detail', ticket_id=ticket_id))

    offered_price = request.form.get('offered_price_per_kg', type=float)
    if not offered_price or offered_price <= 0:
        flash("Please enter a valid price per kg greater than 0.", "warning")
        return redirect(url_for('buyer.ticket_detail', ticket_id=ticket_id))

    success, msg = OfferService.submit_or_update_offer(
        buyer_id=current_user.id,
        ticket_id=ticket_id,
        offered_price_per_kg=offered_price
    )

    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for('buyer.ticket_detail', ticket_id=ticket_id))

@buyer_bp.route('/offers/<int:offer_id>/withdraw', methods=['POST'])
@login_required
@buyer_required
def withdraw_offer(offer_id):
    success, msg = OfferService.withdraw_offer(buyer_id=current_user.id, offer_id=offer_id)
    if success:
        flash(msg, "info")
    else:
        flash(msg, "warning")
    return redirect(url_for('buyer.my_offers'))

@buyer_bp.route('/offers')
@login_required
@buyer_required
def my_offers():
    status = request.args.get('status', 'all')
    query = BuyerOffer.query.filter_by(buyer_id=current_user.id)

    if status != 'all':
        query = query.filter_by(offer_status=status)

    offers = query.order_by(BuyerOffer.created_at.desc()).all()
    return render_template('buyer/my_offers.html', offers=offers, current_status=status)

@buyer_bp.route('/prices', methods=['GET', 'POST'])
@login_required
@buyer_required
def manage_prices():
    categories = GarbageCategory.query.filter_by(status='active').order_by(GarbageCategory.category_name).all()

    if request.method == 'POST':
        # Batch update prices
        for cat in categories:
            price_val = request.form.get(f'price_{cat.id}', type=float)
            if price_val is not None and price_val >= 0:
                price_record = BuyerPrice.query.filter_by(buyer_id=current_user.id, category_id=cat.id).first()
                if not price_record:
                    price_record = BuyerPrice(buyer_id=current_user.id, category_id=cat.id, price_per_kg=price_val)
                    db.session.add(price_record)
                else:
                    price_record.price_per_kg = price_val
        db.session.commit()
        flash("Your purchasing price rates have been updated successfully!", "success")
        return redirect(url_for('buyer.manage_prices'))

    existing_rates = {bp.category_id: float(bp.price_per_kg) for bp in current_user.buyer_prices}
    return render_template('buyer/prices.html', categories=categories, existing_rates=existing_rates)

@buyer_bp.route('/pickups')
@login_required
@buyer_required
def pickups():
    buyer_id = current_user.id
    pickups_list = Pickup.query.filter_by(buyer_id=buyer_id).order_by(Pickup.pickup_date.asc()).all()
    return render_template('buyer/pickups.html', pickups=pickups_list)

@buyer_bp.route('/pickups/<int:pickup_id>/status', methods=['POST'])
@login_required
@buyer_required
def update_pickup_status(pickup_id):
    pickup = Pickup.query.filter_by(id=pickup_id, buyer_id=current_user.id).first_or_404()
    new_status = request.form.get('pickup_status')
    valid_statuses = ['Scheduled', 'Buyer On The Way', 'Arrived', 'Garbage Collected', 'Cancelled']

    if new_status in valid_statuses:
        pickup.pickup_status = new_status
        db.session.commit()
        flash(f"Pickup status updated to '{new_status}'.", "info")
    else:
        flash("Invalid pickup status specified.", "warning")

    return redirect(url_for('buyer.pickups'))

@buyer_bp.route('/pickups/<int:pickup_id>/complete', methods=['POST'])
@login_required
@buyer_required
def complete_pickup_and_pay(pickup_id):
    pickup = Pickup.query.filter_by(id=pickup_id, buyer_id=current_user.id).first_or_404()
    actual_weight = request.form.get('actual_weight', type=float)
    payment_method = request.form.get('payment_method', 'Cash')
    collection_notes = request.form.get('collection_notes', '').strip()

    if not actual_weight or actual_weight <= 0:
        flash("Please enter a valid verified actual weight (kg) greater than 0.", "warning")
        return redirect(url_for('buyer.pickups'))

    success, msg = PaymentService.complete_collection_and_payment(
        buyer_id=current_user.id,
        ticket_id=pickup.ticket_id,
        actual_weight=actual_weight,
        payment_method=payment_method,
        collection_notes=collection_notes
    )

    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for('buyer.pickups'))

@buyer_bp.route('/purchases')
@login_required
@buyer_required
def purchases():
    buyer_id = current_user.id
    transactions = Transaction.query.filter_by(buyer_id=buyer_id).order_by(Transaction.transaction_date.desc()).all()
    total_spent = sum([float(t.total_amount) for t in transactions])
    total_kg = sum([float(t.actual_weight) for t in transactions])

    return render_template(
        'buyer/purchases.html',
        transactions=transactions,
        total_spent=total_spent,
        total_kg=total_kg
    )

@buyer_bp.route('/reviews')
@login_required
@buyer_required
def reviews():
    buyer_id = current_user.id
    received_reviews = Review.query.filter_by(buyer_id=buyer_id).order_by(Review.created_at.desc()).all()
    return render_template('buyer/reviews.html', reviews=received_reviews)

@buyer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@buyer_required
def profile():
    profile = current_user.buyer_profile
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        shop_name = request.form.get('shop_name', '').strip()
        shop_address = request.form.get('shop_address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        service_area = request.form.get('service_area', '').strip()

        if not all([full_name, phone, shop_name, shop_address, city, state, pincode, service_area]):
            flash("All profile fields are required.", "warning")
        else:
            current_user.full_name = full_name
            current_user.phone = phone
            profile.shop_name = shop_name
            profile.shop_address = shop_address
            profile.city = city
            profile.state = state
            profile.pincode = pincode
            profile.service_area = service_area
            db.session.commit()
            flash("Shop profile updated successfully!", "success")
            return redirect(url_for('buyer.profile'))

    return render_template('buyer/profile.html', profile=profile)

