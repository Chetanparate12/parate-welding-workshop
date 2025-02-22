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

        total = float(data['total'])
        amount_paid = float(data['amount_paid'])

        # Determine payment status
        payment_status = 'pending'
        if amount_paid >= total:
            payment_status = 'paid'
        elif amount_paid > 0:
            payment_status = 'partial'

        new_bill = Bill(
            bill_number=bill_number,
            client_name=data['client_name'],
            phone_number=data['phone_number'],
            date=datetime.utcnow(),
            items=items,
            subtotal=float(data['subtotal']),
            total=total,
            amount_paid=amount_paid,
            payment_status=payment_status,
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

@app.route('/edit_payment/<int:bill_id>')
def edit_payment(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return render_template('edit_payment.html', bill=bill)

@app.route('/update_payment/<int:bill_id>', methods=['POST'])
def update_payment(bill_id):
    try:
        bill = Bill.query.get_or_404(bill_id)
        new_payment = float(request.form['new_payment'])

        # Validate payment amount
        pending_amount = bill.total - bill.amount_paid
        if new_payment <= 0 or new_payment > pending_amount:
            flash('Invalid payment amount', 'danger')
            return redirect(url_for('edit_payment', bill_id=bill.id))

        # Update payment information
        bill.amount_paid += new_payment

        # Update payment status
        if bill.amount_paid >= bill.total:
            bill.payment_status = 'paid'
        else:
            bill.payment_status = 'partial'

        db.session.commit()

        # Generate updated PDF
        generate_pdf(bill, bill.pdf_path)

        flash('Payment updated successfully!', 'success')
        return redirect(url_for('bills'))

    except Exception as e:
        app.logger.error(f"Error updating payment: {str(e)}")
        flash('Error updating payment. Please try again.', 'danger')
        return redirect(url_for('edit_payment', bill_id=bill_id))