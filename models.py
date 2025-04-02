from datetime import datetime
from app import db

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(20), unique=True, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.Column(db.JSON, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(200), nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid
    
class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id', ondelete='SET NULL'), nullable=True)
    bill_number = db.Column(db.String(20), nullable=False) 
    client_name = db.Column(db.String(100), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    deleted = db.Column(db.Boolean, default=False)  # To mark records as deleted without actually removing them