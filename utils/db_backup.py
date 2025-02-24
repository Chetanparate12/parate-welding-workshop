
from replit import db
from models import Bill
from app import app

def backup_bill_to_replit_db(bill):
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
