from datetime import datetime
from . import db

class SellingTicket(db.Model):
    __tablename__ = 'selling_tickets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('garbage_categories.id', ondelete='RESTRICT'), nullable=False, index=True)
    estimated_quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(10), default='kg')
    garbage_condition = db.Column(db.String(30), default='Clean')  # 'Clean', 'Sorted', 'Unsorted'
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    pickup_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(15), nullable=False)
    preferred_pickup_date = db.Column(db.Date, nullable=False)
    preferred_pickup_time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(30), default='Open', index=True)  # 'Open', 'Offer Accepted', 'Scheduled', 'In Progress', 'Completed', 'Cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    offers = db.relationship('BuyerOffer', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    pickup = db.relationship('Pickup', backref='ticket', uselist=False, cascade='all, delete-orphan')
    transaction = db.relationship('Transaction', backref='ticket', uselist=False, cascade='all, delete-orphan')
    review = db.relationship('Review', backref='ticket', uselist=False, cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='ticket', lazy='dynamic')

    @property
    def has_accepted_offer(self):
        return self.status in ['Offer Accepted', 'Scheduled', 'In Progress', 'Completed']

    @property
    def can_be_edited_or_cancelled(self):
        return self.status == 'Open'

    def __repr__(self):
        return f"<SellingTicket {self.ticket_number} ({self.status})>"

