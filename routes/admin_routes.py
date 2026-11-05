from decimal import Decimal
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models import (
    db, User, SellerProfile, BuyerProfile, GarbageCategory,
    SellingTicket, BuyerOffer, Pickup, Transaction, Complaint
)
from services.notification_service import NotificationService
from routes.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_sellers = User.query.filter_by(role='seller').count()
    total_buyers = User.query.filter_by(role='buyer').count()
    pending_buyers = BuyerProfile.query.filter_by(verification_status='pending').count()
    total_tickets = SellingTicket.query.count()
    completed_collections = SellingTicket.query.filter_by(status='Completed').count()

    total_kg_query = db.session.query(db.func.sum(Transaction.actual_weight)).filter(
        Transaction.payment_status == 'Completed'
    ).scalar()
    total_collected_kg = float(total_kg_query or 0.0)

    total_trans_query = db.session.query(db.func.sum(Transaction.total_amount)).filter(
        Transaction.payment_status == 'Completed'
    ).scalar()
    total_transactions_amount = float(total_trans_query or 0.0)

    open_complaints = Complaint.query.filter(Complaint.complaint_status.in_(['Open', 'Under Review'])).count()

    # Category recycling breakdown
    category_breakdown = db.session.query(
        GarbageCategory.category_name,
        db.func.sum(Transaction.actual_weight)
    ).join(SellingTicket, SellingTicket.category_id == GarbageCategory.id)\
     .join(Transaction, Transaction.ticket_id == SellingTicket.id)\
     .filter(Transaction.payment_status == 'Completed')\
     .group_by(GarbageCategory.category_name).all()

    cat_labels = [c[0] for c in category_breakdown] if category_breakdown else ['General Recyclables']
    cat_values = [float(c[1]) for c in category_breakdown] if category_breakdown else [0]

    # Monthly recycling weight chart
    month_expr = db.func.strftime('%Y-%m', Transaction.transaction_date) if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI'] \
                 else db.func.date_format(Transaction.transaction_date, '%Y-%m')
    
    monthly_stats = db.session.query(
        month_expr,
        db.func.sum(Transaction.actual_weight),
        db.func.sum(Transaction.total_amount)
    ).filter(Transaction.payment_status == 'Completed')\
     .group_by(month_expr).order_by(month_expr.asc()).limit(6).all()

    month_labels = [m[0] for m in monthly_stats] if monthly_stats else ['Current']
    month_weights = [float(m[1]) for m in monthly_stats] if monthly_stats else [0]
    month_amounts = [float(m[2]) for m in monthly_stats] if monthly_stats else [0]

    recent_users = User.query.filter(User.role != 'admin').order_by(User.created_at.desc()).limit(5).all()
    recent_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_sellers=total_sellers,
        total_buyers=total_buyers,
        pending_buyers=pending_buyers,
        total_tickets=total_tickets,
        completed_collections=completed_collections,
        total_collected_kg=total_collected_kg,
        total_transactions_amount=total_transactions_amount,
        open_complaints=open_complaints,
        recent_users=recent_users,
        recent_transactions=recent_transactions,
        cat_labels=cat_labels,
        cat_values=cat_values,
        month_labels=month_labels,
        month_weights=month_weights,
        month_amounts=month_amounts
    )

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role_filter = request.args.get('role', 'all')
    search = request.args.get('q', '').strip()

    query = User.query.filter(User.role != 'admin')
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.phone.ilike(f"%{search}%"))
        )

    users_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list, current_role=role_filter, search_query=search)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot modify admin status.", "danger")
        return redirect(url_for('admin.users'))

    user.account_status = 'suspended' if user.account_status == 'active' else 'active'
    db.session.commit()
    flash(f"User {user.email} status updated to '{user.account_status}'.", "info")
    return redirect(url_for('admin.users'))

@admin_bp.route('/buyers/verification')
@login_required
@admin_required
def buyers_verification():
    status = request.args.get('status', 'all')
    query = BuyerProfile.query.join(User)

    if status != 'all':
        query = query.filter(BuyerProfile.verification_status == status)

    buyers = query.order_by(User.created_at.desc()).all()
    return render_template('admin/buyers.html', buyers=buyers, current_status=status)

@admin_bp.route('/buyers/<int:profile_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_buyer(profile_id):
    profile = BuyerProfile.query.get_or_404(profile_id)
    action = request.form.get('action', 'verified')  # 'verified' or 'rejected'

    if action in ['verified', 'rejected']:
        profile.verification_status = action
        db.session.commit()

        msg = "Your scrap dealer profile has been verified! You can now place offers on garbage selling tickets." if action == 'verified' \
              else "Your scrap dealer registration was not approved. Please contact admin support."
        NotificationService.send(
            user_id=profile.user_id,
            title=f"Account Verification: {action.capitalize()}",
            message=msg
        )
        flash(f"Buyer '{profile.shop_name}' marked as {action}.", "success")
    return redirect(url_for('admin.buyers_verification'))

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    if request.method == 'POST':
        category_name = request.form.get('category_name', '').strip()
        description = request.form.get('description', '').strip()

        if not category_name:
            flash("Category name is required.", "warning")
        elif GarbageCategory.query.filter_by(category_name=category_name).first():
            flash("A category with this name already exists.", "warning")
        else:
            cat = GarbageCategory(
                category_name=category_name,
                description=description,
                status='active'
            )
            db.session.add(cat)
            db.session.commit()
            flash(f"Garbage category '{category_name}' added successfully!", "success")
            return redirect(url_for('admin.categories'))

    all_categories = GarbageCategory.query.order_by(GarbageCategory.category_name).all()
    return render_template('admin/categories.html', categories=all_categories)

@admin_bp.route('/categories/<int:cat_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_category(cat_id):
    cat = GarbageCategory.query.get_or_404(cat_id)
    cat.status = 'inactive' if cat.status == 'active' else 'active'
    db.session.commit()
    flash(f"Category '{cat.category_name}' status set to {cat.status}.", "info")
    return redirect(url_for('admin.categories'))

@admin_bp.route('/tickets')
@login_required
@admin_required
def tickets():
    status = request.args.get('status', 'all')
    query = SellingTicket.query

    if status != 'all':
        query = query.filter_by(status=status)

    all_tickets = query.order_by(SellingTicket.created_at.desc()).all()
    return render_template('admin/tickets.html', tickets=all_tickets, current_status=status)

@admin_bp.route('/transactions')
@login_required
@admin_required
def transactions():
    all_transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    total_amount = sum([float(t.total_amount) for t in all_transactions])
    total_weight = sum([float(t.actual_weight) for t in all_transactions])

    return render_template(
        'admin/transactions.html',
        transactions=all_transactions,
        total_amount=total_amount,
        total_weight=total_weight
    )

@admin_bp.route('/complaints', methods=['GET', 'POST'])
@login_required
@admin_required
def complaints():
    if request.method == 'POST':
        complaint_id = request.form.get('complaint_id', type=int)
        admin_response = request.form.get('admin_response', '').strip()
        status = request.form.get('complaint_status', 'Resolved')

        complaint = Complaint.query.get_or_404(complaint_id)
        complaint.admin_response = admin_response
        complaint.complaint_status = status
        db.session.commit()

        NotificationService.send(
            user_id=complaint.user_id,
            title=f"Complaint #{complaint.id} Update",
            message=f"Admin responded: '{admin_response}' (Status: {status})"
        )
        flash(f"Complaint #{complaint.id} responded and updated to '{status}'.", "success")
        return redirect(url_for('admin.complaints'))

    all_complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    return render_template('admin/complaints.html', complaints=all_complaints)

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    total_sellers = User.query.filter_by(role='seller').count()
    total_buyers = User.query.filter_by(role='buyer').count()
    total_tickets = SellingTicket.query.count()
    total_completed = SellingTicket.query.filter_by(status='Completed').count()

    total_kg = db.session.query(db.func.sum(Transaction.actual_weight)).scalar() or 0
    total_revenue = db.session.query(db.func.sum(Transaction.total_amount)).scalar() or 0

    category_summary = db.session.query(
        GarbageCategory.category_name,
        db.func.count(SellingTicket.id),
        db.func.sum(Transaction.actual_weight),
        db.func.sum(Transaction.total_amount)
    ).outerjoin(SellingTicket, SellingTicket.category_id == GarbageCategory.id)\
     .outerjoin(Transaction, Transaction.ticket_id == SellingTicket.id)\
     .group_by(GarbageCategory.category_name).all()

    return render_template(
        'admin/reports.html',
        total_sellers=total_sellers,
        total_buyers=total_buyers,
        total_tickets=total_tickets,
        total_completed=total_completed,
        total_kg=float(total_kg),
        total_revenue=float(total_revenue),
        category_summary=category_summary
    )
