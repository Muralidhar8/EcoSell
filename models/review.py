from datetime import datetime
from . import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('selling_tickets.id', ondelete='CASCADE'), nullable=False, unique=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='received_reviews')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='given_reviews')

    def __repr__(self):
        return f"<Review ticket={self.ticket_id} rating={self.rating}>"

