from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def seller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login'))
        if not current_user.is_seller:
            flash("Access denied. Seller account required.", "danger")
            abort(403)
        if not current_user.is_active:
            flash("Your account is currently suspended. Please contact admin.", "danger")
            return redirect(url_for('auth.logout'))
        return f(*args, **kwargs)
    return decorated_function

def buyer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login'))
        if not current_user.is_buyer:
            flash("Access denied. Scrap Dealer / Buyer account required.", "danger")
            abort(403)
        if not current_user.is_active:
            flash("Your account is currently suspended. Please contact admin.", "danger")
            return redirect(url_for('auth.logout'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in with admin credentials.", "warning")
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash("Access denied. Admin privileges required.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

