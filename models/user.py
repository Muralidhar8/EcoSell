from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(25), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # 'seller', 'buyer', 'admin'
    account_status = db.Column(db.String(20), default='active')  # 'active', 'pending', 'suspended'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    seller_profile = db.relationship('SellerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    buyer_profile = db.relationship('BuyerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    selling_tickets = db.relationship('SellingTicket', backref='seller', lazy='dynamic', cascade='all, delete-orphan')
    buyer_offers = db.relationship('BuyerOffer', backref='buyer', lazy='dynamic', cascade='all, delete-orphan')
    buyer_prices = db.relationship('BuyerPrice', backref='buyer', lazy='dynamic', cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan', order_by='Notification.created_at.desc()')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_seller(self):
        return self.role == 'seller'

    @property
    def is_buyer(self):
        return self.role == 'buyer'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_active(self):
        return self.account_status == 'active'

    @property
    def is_verified_buyer(self):
        if not self.is_buyer or not self.buyer_profile:
            return False
        return self.buyer_profile.verification_status == 'verified'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

