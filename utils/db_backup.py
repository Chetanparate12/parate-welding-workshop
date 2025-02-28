
from models import Bill
from app import app
import logging

def backup_bill_to_replit_db(bill):
    try:
        from replit import db
        with app.app_context():
            key = f"bill_{bill.bill_number}"
            db[key] = {
                'id': bill.id,
                'bill_number': bill.bill_number,
                'client_name': bill.client_name,
                'phone_number': bill.phone_number,
                'date': bill.date.isoformat(),
                'items': bill.items,
                'subtotal': bill.subtotal,
                'total': bill.total,
                'pdf_path': bill.pdf_path,
                'amount_paid': bill.amount_paid,
                'payment_status': bill.payment_status
            }
    except Exception as e:
        logging.error(f"Failed to backup bill to Replit DB: {str(e)}")
        # Continue even if Replit DB fails

def delete_bill_from_replit_db(bill_number):
    try:
        from replit import db
        key = f"bill_{bill_number}"
        if key in db:
            del db[key]
    except Exception as e:
        logging.error(f"Failed to delete bill from Replit DB: {str(e)}")
        # Continue even if Replit DB fails
