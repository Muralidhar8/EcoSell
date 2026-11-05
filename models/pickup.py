from datetime import datetime
from . import db

class Pickup(db.Model):
    __tablename__ = 'pickups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('selling_tickets.id', ondelete='CASCADE'), nullable=False, unique=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    pickup_date = db.Column(db.Date, nullable=False)
    pickup_time = db.Column(db.String(50), nullable=False)
    actual_weight = db.Column(db.Numeric(10, 2), nullable=True)
    pickup_status = db.Column(
        db.String(30),
        default='Scheduled',
        index=True
    )  # 'Pending', 'Scheduled', 'Buyer On The Way', 'Arrived', 'Garbage Collected', 'Completed', 'Cancelled'
    collection_notes = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_pickups')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_pickups')

    def __repr__(self):
        return f"<Pickup ticket={self.ticket_id} buyer={self.buyer_id} status={self.pickup_status}>"

