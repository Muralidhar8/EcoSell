import os
import uuid
from decimal import Decimal
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import (
    db, User, SellerProfile, BuyerProfile, GarbageCategory, SellingTicket,
    BuyerOffer, Pickup, Transaction, Review, Complaint, Notification
)
from services.ticket_service import TicketService
from services.offer_service import OfferService
from routes.decorators import seller_required

seller_bp = Blueprint('seller', __name__, url_prefix='/seller')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@seller_bp.route('/dashboard')
@login_required
@seller_required
def dashboard():
    seller_id = current_user.id

    # Dynamic metrics fetched from database
    total_tickets = SellingTicket.query.filter_by(seller_id=seller_id).count()
    open_tickets = SellingTicket.query.filter_by(seller_id=seller_id, status='Open').count()
    completed_sales = SellingTicket.query.filter_by(seller_id=seller_id, status='Completed').count()
    
    # Offers received on all seller's tickets
    offers_received = BuyerOffer.query.join(SellingTicket).filter(
        SellingTicket.seller_id == seller_id
    ).count()

    # Total earnings from completed transactions
    earnings_query = db.session.query(db.func.sum(Transaction.total_amount)).filter(
        Transaction.seller_id == seller_id,
        Transaction.payment_status == 'Completed'
    ).scalar()
    total_earnings = float(earnings_query or 0.0)

    # Total weight recycled in KG
    total_weight_query = db.session.query(db.func.sum(Transaction.actual_weight)).filter(
        Transaction.seller_id == seller_id,
        Transaction.payment_status == 'Completed'
    ).scalar()
    total_weight_kg = float(total_weight_query or 0.0)

    # Recent tickets
    recent_tickets = SellingTicket.query.filter_by(seller_id=seller_id).order_by(
        SellingTicket.created_at.desc()
    ).limit(5).all()

    # Recent active pickups
    recent_pickups = Pickup.query.filter_by(seller_id=seller_id).order_by(
        Pickup.pickup_date.desc()
    ).limit(4).all()

    # Monthly earnings breakdown for Chart.js
    month_expr = db.func.strftime('%Y-%m', Transaction.transaction_date) if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI'] \
                 else db.func.date_format(Transaction.transaction_date, '%Y-%m')
    
    monthly_data = db.session.query(
        month_expr,
        db.func.sum(Transaction.total_amount)
    ).filter(
        Transaction.seller_id == seller_id,
        Transaction.payment_status == 'Completed'
    ).group_by(month_expr).order_by(month_expr.asc()).limit(6).all()

    months_labels = [row[0] for row in monthly_data] if monthly_data else ['Current']
    months_values = [float(row[1]) for row in monthly_data] if monthly_data else [0.0]

    return render_template(
        'seller/dashboard.html',
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        offers_received=offers_received,
        completed_sales=completed_sales,
        total_earnings=total_earnings,
        total_weight_kg=total_weight_kg,
        recent_tickets=recent_tickets,
        recent_pickups=recent_pickups,
        chart_labels=months_labels,
        chart_values=months_values
    )

@seller_bp.route('/tickets/create', methods=['GET', 'POST'])
@login_required
@seller_required
def create_ticket():
    categories = GarbageCategory.query.filter_by(status='active').order_by(GarbageCategory.category_name).all()
    profile = current_user.seller_profile

    if request.method == 'POST':
        category_id = request.form.get('category_id', type=int)
        estimated_quantity = request.form.get('estimated_quantity', type=float)
        garbage_condition = request.form.get('garbage_condition', 'Clean')
        description = request.form.get('description', '').strip()
        pickup_address = request.form.get('pickup_address', '').strip()
        city = request.form.get('city', '').strip()
        pincode = request.form.get('pincode', '').strip()
        pickup_date_str = request.form.get('preferred_pickup_date', '')
        pickup_time = request.form.get('preferred_pickup_time', '').strip()

        # Validation
        if not category_id or not estimated_quantity or estimated_quantity <= 0:
            flash("Please choose a valid category and specify quantity greater than 0 kg.", "warning")
            return render_template('seller/create_ticket.html', categories=categories, profile=profile)

        if not all([pickup_address, city, pincode, pickup_date_str, pickup_time]):
            flash("Please fill in pickup location and preferred date & time slot.", "warning")
            return render_template('seller/create_ticket.html', categories=categories, profile=profile)

        try:
            pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
            if pickup_date < date.today():
                flash("Preferred pickup date cannot be in the past.", "warning")
                return render_template('seller/create_ticket.html', categories=categories, profile=profile)
        except ValueError:
            flash("Invalid date format.", "warning")
            return render_template('seller/create_ticket.html', categories=categories, profile=profile)

        # Handle Image Upload
        filename = None
        if 'garbage_image' in request.files:
            file = request.files['garbage_image']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"ticket_{uuid.uuid4().hex[:12]}.{ext}"
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)

        ticket = TicketService.create_ticket(
            seller_id=current_user.id,
            category_id=category_id,
            estimated_quantity=estimated_quantity,
            garbage_condition=garbage_condition,
            description=description,
            pickup_address=pickup_address,
            city=city,
            pincode=pincode,
            preferred_pickup_date=pickup_date,
            preferred_pickup_time=pickup_time,
            image_filename=filename
        )

        flash(f"Ticket {ticket.ticket_number} created successfully! Buyers will start placing competitive bids.", "success")
        return redirect(url_for('seller.ticket_detail', ticket_id=ticket.id))

    return render_template('seller/create_ticket.html', categories=categories, profile=profile)

@seller_bp.route('/tickets')
@login_required
@seller_required
def my_tickets():
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('q', '').strip()

    query = SellingTicket.query.filter_by(seller_id=current_user.id)

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if search_query:
        query = query.filter(
            (SellingTicket.ticket_number.ilike(f"%{search_query}%")) |
            (SellingTicket.description.ilike(f"%{search_query}%")) |
            (SellingTicket.city.ilike(f"%{search_query}%"))
        )

    tickets = query.order_by(SellingTicket.created_at.desc()).all()
    return render_template('seller/my_tickets.html', tickets=tickets, current_filter=status_filter, search_query=search_query)

@seller_bp.route('/tickets/<int:ticket_id>')
@login_required
@seller_required
def ticket_detail(ticket_id):
    ticket = SellingTicket.query.filter_by(id=ticket_id, seller_id=current_user.id).first_or_404()
    offers = BuyerOffer.query.filter_by(ticket_id=ticket.id).order_by(BuyerOffer.offered_price_per_kg.desc()).all()
    pickup = Pickup.query.filter_by(ticket_id=ticket.id).first()
    transaction = Transaction.query.filter_by(ticket_id=ticket.id).first()
    review = Review.query.filter_by(ticket_id=ticket.id).first()

    return render_template(
        'seller/ticket_detail.html',
        ticket=ticket,
        offers=offers,
        pickup=pickup,
        transaction=transaction,
        review=review
    )

@seller_bp.route('/tickets/<int:ticket_id>/cancel', methods=['POST'])
@login_required
@seller_required
def cancel_ticket(ticket_id):
    ticket = SellingTicket.query.filter_by(id=ticket_id, seller_id=current_user.id).first_or_404()
    if not ticket.can_be_edited_or_cancelled:
        flash("Cannot cancel a ticket once an offer has been accepted or scheduled.", "danger")
        return redirect(url_for('seller.ticket_detail', ticket_id=ticket.id))

    ticket.status = 'Cancelled'
    # Close any pending offers
    BuyerOffer.query.filter_by(ticket_id=ticket.id, offer_status='Pending').update({'offer_status': 'Closed'})
    db.session.commit()

    flash(f"Ticket {ticket.ticket_number} has been cancelled.", "info")
    return redirect(url_for('seller.my_tickets'))

@seller_bp.route('/offers/<int:offer_id>/accept', methods=['POST'])
@login_required
@seller_required
def accept_offer(offer_id):
    success, msg = OfferService.accept_offer(seller_id=current_user.id, offer_id=offer_id)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    offer = BuyerOffer.query.get(offer_id)
    if offer:
        return redirect(url_for('seller.ticket_detail', ticket_id=offer.ticket_id))
    return redirect(url_for('seller.my_tickets'))

@seller_bp.route('/offers/<int:offer_id>/reject', methods=['POST'])
@login_required
@seller_required
def reject_offer(offer_id):
    offer = BuyerOffer.query.get_or_404(offer_id)
    ticket = SellingTicket.query.filter_by(id=offer.ticket_id, seller_id=current_user.id).first_or_404()

    if offer.offer_status == 'Pending':
        offer.offer_status = 'Rejected'
        db.session.commit()
        flash("Offer has been marked as rejected.", "info")
    else:
        flash("Offer cannot be rejected in its current status.", "warning")

    return redirect(url_for('seller.ticket_detail', ticket_id=ticket.id))

@seller_bp.route('/pickups')
@login_required
@seller_required
def pickups():
    seller_id = current_user.id
    pickups_list = Pickup.query.filter_by(seller_id=seller_id).order_by(Pickup.pickup_date.desc()).all()
    return render_template('seller/pickups.html', pickups=pickups_list)

@seller_bp.route('/earnings')
@login_required
@seller_required
def earnings():
    seller_id = current_user.id
    transactions = Transaction.query.filter_by(seller_id=seller_id).order_by(Transaction.transaction_date.desc()).all()
    
    total_earned = sum([float(t.total_amount) for t in transactions])
    total_weight = sum([float(t.actual_weight) for t in transactions])

    return render_template(
        'seller/earnings.html',
        transactions=transactions,
        total_earned=total_earned,
        total_weight=total_weight
    )

@seller_bp.route('/reviews/submit/<int:ticket_id>', methods=['POST'])
@login_required
@seller_required
def submit_review(ticket_id):
    ticket = SellingTicket.query.filter_by(id=ticket_id, seller_id=current_user.id).first_or_404()
    if ticket.status != 'Completed':
        flash("Reviews can only be submitted after garbage collection is completed.", "warning")
        return redirect(url_for('seller.ticket_detail', ticket_id=ticket.id))

    pickup = Pickup.query.filter_by(ticket_id=ticket.id).first()
    if not pickup:
        flash("Pickup details not found.", "danger")
        return redirect(url_for('seller.ticket_detail', ticket_id=ticket.id))

    rating = request.form.get('rating', type=int)
    review_text = request.form.get('review_text', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash("Please provide a valid rating between 1 and 5 stars.", "warning")
        return redirect(url_for('seller.ticket_detail', ticket_id=ticket.id))

    existing = Review.query.filter_by(ticket_id=ticket.id).first()
    if existing:
        existing.rating = rating
        existing.review_text = review_text
        db.session.commit()
        flash("Review updated successfully!", "success")
    else:
        review = Review(
            ticket_id=ticket.id,
            seller_id=current_user.id,
            buyer_id=pickup.buyer_id,
            rating=rating,
            review_text=review_text
        )
        db.session.add(review)

        # Update Buyer's aggregate average rating
        all_reviews = Review.query.filter_by(buyer_id=pickup.buyer_id).all()
        avg_rating = sum([r.rating for r in all_reviews] + [rating]) / (len(all_reviews) + 1)
        buyer_profile = BuyerProfile.query.filter_by(user_id=pickup.buyer_id).first()
        if buyer_profile:
            buyer_profile.rating = round(Decimal(str(avg_rating)), 2)

        db.session.commit()
        flash("Thank you for reviewing the scrap dealer!", "success")

    return redirect(url_for('seller.ticket_detail', ticket_id=ticket.id))

@seller_bp.route('/complaints', methods=['GET', 'POST'])
@login_required
@seller_required
def complaints():
    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id', type=int)
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()

        if not subject or not description:
            flash("Please provide both subject and detailed description of the complaint.", "warning")
        else:
            complaint = Complaint(
                user_id=current_user.id,
                ticket_id=ticket_id if ticket_id else None,
                subject=subject,
                description=description,
                complaint_status='Open'
            )
            db.session.add(complaint)
            db.session.commit()
            flash("Your complaint has been submitted. Our admin support team will review it shortly.", "success")
            return redirect(url_for('seller.complaints'))

    user_complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    user_tickets = SellingTicket.query.filter_by(seller_id=current_user.id).order_by(SellingTicket.created_at.desc()).all()
    return render_template('seller/complaints.html', complaints=user_complaints, tickets=user_tickets)

@seller_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@seller_required
def profile():
    profile = current_user.seller_profile
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()

        if not all([full_name, phone, address, city, state, pincode]):
            flash("All profile fields are required.", "warning")
        else:
            current_user.full_name = full_name
            current_user.phone = phone
            profile.address = address
            profile.city = city
            profile.state = state
            profile.pincode = pincode
            db.session.commit()
            flash("Profile details updated successfully!", "success")
            return redirect(url_for('seller.profile'))

    return render_template('seller/profile.html', profile=profile)
