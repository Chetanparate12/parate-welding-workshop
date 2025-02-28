import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key")

# Remove the existing SQLite database file if it exists
sqlite_path = "instance/bills.db"
if os.path.exists(sqlite_path):
    os.remove(sqlite_path)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bills.db")

# Restore data from Replit DB if SQLite is empty
def restore_from_replit_db():
    from models import Bill
    from replit import db
    import json
    from datetime import datetime
    
    # Only restore if there are no bills in SQLite but there are in Replit DB
    if Bill.query.count() == 0:
        bill_keys = [k for k in db.keys() if k.startswith('bill_')]
        if bill_keys:
            for key in bill_keys:
                bill_data = db[key]
                # Create Bill object from Replit DB data
                new_bill = Bill(
                    bill_number=bill_data['bill_number'],
                    client_name=bill_data['client_name'],
                    phone_number=bill_data['phone_number'],
                    date=datetime.fromisoformat(bill_data['date']),
                    items=bill_data['items'],
                    subtotal=bill_data['subtotal'],
                    total=bill_data['total'],
                    pdf_path=bill_data['pdf_path'],
                    amount_paid=bill_data['amount_paid'],
                    payment_status=bill_data['payment_status']
                )
                db.session.add(new_bill)
            db.session.commit()

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

from routes import *  # noqa: F401

with app.app_context():
    db.create_all()
    restore_from_replit_db()