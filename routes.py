import os
from datetime import datetime
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app, db
from models import Bill
from utils.pdf_generator import generate_pdf

UPLOAD_FOLDER = 'generated_pdfs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bills')
def bills():
    all_bills = Bill.query.order_by(Bill.date.desc()).all()
    return render_template('bills.html', bills=all_bills)

@app.route('/generate_bill', methods=['POST'])
def generate_bill():
    try:
        data = request.form
        items = []

        for i in range(len(request.form.getlist('item_name[]'))):
            items.append({
                'name': request.form.getlist('item_name[]')[i],
                'quantity': float(request.form.getlist('quantity[]')[i]),
                'price': float(request.form.getlist('price[]')[i]),
                'amount': float(request.form.getlist('amount[]')[i])
            })

        bill_number = f"FAB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        pdf_filename = f"{bill_number}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)

        new_bill = Bill(
            bill_number=bill_number,
            client_name=data['client_name'],
            phone_number=data['phone_number'],
            date=datetime.utcnow(),  # Explicitly set the date
            items=items,
            subtotal=float(data['subtotal']),
            total=float(data['total']),
            pdf_path=pdf_path
        )

        # Generate PDF before saving to database to catch any PDF generation errors
        generate_pdf(new_bill, pdf_path)

        db.session.add(new_bill)
        db.session.commit()

        flash('Bill generated successfully!', 'success')
        return redirect(url_for('bills'))

    except Exception as e:
        app.logger.error(f"Error generating bill: {str(e)}")
        flash('Error generating bill. Please try again.', 'danger')
        return redirect(url_for('index'))

@app.route('/download_pdf/<int:bill_id>')
def download_pdf(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return send_file(bill.pdf_path, as_attachment=True)