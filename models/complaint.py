from datetime import datetime
from . import db

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('selling_tickets.id', ondelete='SET NULL'), nullable=True)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    complaint_status = db.Column(db.String(30), default='Open', index=True)  # 'Open', 'Under Review', 'Resolved', 'Closed'
    admin_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Complaint #{self.id} user={self.user_id} status={self.complaint_status}>"

