from datetime import datetime
from . import db

class BuyerPrice(db.Model):
    __tablename__ = 'buyer_prices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('garbage_categories.id', ondelete='CASCADE'), nullable=False)
    price_per_kg = db.Column(db.Numeric(10, 2), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('buyer_id', 'category_id', name='uq_buyer_category'),
    )

    def __repr__(self):
        return f"<BuyerPrice buyer={self.buyer_id} category={self.category_id} rate={self.price_per_kg}>"


class BuyerOffer(db.Model):
    __tablename__ = 'buyer_offers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('selling_tickets.id', ondelete='CASCADE'), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    offered_price_per_kg = db.Column(db.Numeric(10, 2), nullable=False)
    estimated_total = db.Column(db.Numeric(10, 2), nullable=False)
    offer_status = db.Column(db.String(20), default='Pending', index=True)  # 'Pending', 'Accepted', 'Rejected', 'Withdrawn', 'Closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BuyerOffer #{self.id} ticket={self.ticket_id} buyer={self.buyer_id} rate={self.offered_price_per_kg} status={self.offer_status}>"

