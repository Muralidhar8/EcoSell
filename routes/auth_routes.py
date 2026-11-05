from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, SellerProfile, BuyerProfile, Notification
from services.notification_service import NotificationService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_seller:
            return redirect(url_for('seller.dashboard'))
        elif current_user.is_buyer:
            return redirect(url_for('buyer.dashboard'))
        elif current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please verify your credentials.", "danger")
            return render_template('auth/login.html')

        if not user.is_active:
            flash("Your account has been suspended or is currently inactive. Please contact support.", "danger")
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.full_name}!", "success")

        # Redirect according to role or 'next' param
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        if user.is_seller:
            return redirect(url_for('seller.dashboard'))
        elif user.is_buyer:
            return redirect(url_for('buyer.dashboard'))
        elif user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))

    return render_template('auth/login.html')

@auth_bp.route('/register/seller', methods=['GET', 'POST'])
def register_seller():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()

        # Validation
        if not all([full_name, email, phone, password, address, city, state, pincode]):
            flash("Please fill in all required fields.", "warning")
            return render_template('auth/register_seller.html')

        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return render_template('auth/register_seller.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template('auth/register_seller.html')

        if User.query.filter_by(email=email).first():
            flash("An account with this email address already exists.", "danger")
            return render_template('auth/register_seller.html')

        try:
            # Create user
            user = User(
                full_name=full_name,
                email=email,
                phone=phone,
                role='seller',
                account_status='active'
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # Create seller profile
            seller_profile = SellerProfile(
                user_id=user.id,
                address=address,
                city=city,
                state=state,
                pincode=pincode
            )
            db.session.add(seller_profile)
            db.session.commit()

            NotificationService.send(
                user_id=user.id,
                title="Welcome to EcoSell!",
                message="Your seller account is ready! Create your first garbage selling ticket to start earning from recyclable waste."
            )

            login_user(user)
            flash("Registration successful! Welcome to your Seller Dashboard.", "success")
            return redirect(url_for('seller.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {str(e)}", "danger")

    return render_template('auth/register_seller.html')

@auth_bp.route('/register/buyer', methods=['GET', 'POST'])
def register_buyer():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        shop_name = request.form.get('shop_name', '').strip()
        shop_address = request.form.get('shop_address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        service_area = request.form.get('service_area', '').strip()

        # Validation
        if not all([full_name, email, phone, password, shop_name, shop_address, city, state, pincode, service_area]):
            flash("Please fill in all required shopkeeper & buyer fields.", "warning")
            return render_template('auth/register_buyer.html')

        if password != confirm_password:
            flash("Passwords do not match.", "warning")
            return render_template('auth/register_buyer.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template('auth/register_buyer.html')

        if User.query.filter_by(email=email).first():
            flash("An account with this email address already exists.", "danger")
            return render_template('auth/register_buyer.html')

        try:
            # Create user
            user = User(
                full_name=full_name,
                email=email,
                phone=phone,
                role='buyer',
                account_status='active'
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # Create buyer profile (pending verification)
            buyer_profile = BuyerProfile(
                user_id=user.id,
                shop_name=shop_name,
                shop_address=shop_address,
                city=city,
                state=state,
                pincode=pincode,
                service_area=service_area,
                verification_status='pending',
                rating=5.00
            )
            db.session.add(buyer_profile)
            db.session.commit()

            NotificationService.send(
                user_id=user.id,
                title="Registration Submitted for Verification",
                message="Your scrap dealer profile has been submitted. Our administrators will verify your details shortly."
            )

            login_user(user)
            flash("Registration successful! Your shop account is pending admin verification. You can set up your rate list in the meantime.", "info")
            return redirect(url_for('buyer.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Registration failed: {str(e)}", "danger")

    return render_template('auth/register_buyer.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been securely logged out.", "info")
    return redirect(url_for('main.index'))

@auth_bp.route('/notifications/read/<int:notif_id>', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    success = NotificationService.mark_as_read(notif_id, current_user.id)
    return jsonify({'success': success})

@auth_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    success = NotificationService.mark_all_as_read(current_user.id)
    return jsonify({'success': success})

@auth_bp.route('/notifications/unread-count', methods=['GET'])
@login_required
def unread_notifications_count():
    count = NotificationService.get_unread_count(current_user.id)
    return jsonify({'count': count})

