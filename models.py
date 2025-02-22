from datetime import datetime
from app import db

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(20), unique=True, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_address = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.Column(db.JSON, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    pdf_path = db.Column(db.String(200), nullable=False)
