from . import db

class BuyerProfile(db.Model):
    __tablename__ = 'buyer_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    shop_name = db.Column(db.String(150), nullable=False)
    shop_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(15), nullable=False)
    service_area = db.Column(db.String(255), nullable=False)
    verification_status = db.Column(db.String(20), default='pending', index=True)  # 'pending', 'verified', 'rejected'
    rating = db.Column(db.Numeric(3, 2), default=5.00)

    def __repr__(self):
        return f"<BuyerProfile shop='{self.shop_name}' user_id={self.user_id}>"

