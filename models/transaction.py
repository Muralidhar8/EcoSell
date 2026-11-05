from datetime import datetime
from . import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('selling_tickets.id', ondelete='CASCADE'), nullable=False, unique=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    actual_weight = db.Column(db.Numeric(10, 2), nullable=False)
    price_per_kg = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), default='Cash')  # 'Cash', 'UPI', 'Online'
    payment_status = db.Column(db.String(20), default='Completed')  # 'Pending', 'Completed', 'Failed'
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_transactions')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_transactions')

    def __repr__(self):
        return f"<Transaction #{self.id} ticket={self.ticket_id} amount={self.total_amount}>"

