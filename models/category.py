from . import db

class GarbageCategory(db.Model):
    __tablename__ = 'garbage_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active', index=True)  # 'active', 'inactive'

    # Relationships
    tickets = db.relationship('SellingTicket', backref='category', lazy='dynamic')
    buyer_prices = db.relationship('BuyerPrice', backref='category', lazy='dynamic')

    def __repr__(self):
        return f"<GarbageCategory {self.category_name}>"

