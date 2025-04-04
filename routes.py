import os
from datetime import datetime
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app, db

# Login route removed
from models import Bill
from utils.pdf_generator import generate_pdf
from utils.qrcode_generator import generate_bill_qrcode

# Get the application domain for QR code generation
def get_app_domain():
    """Get the application domain for QR code generation"""
    if os.environ.get("REPLIT_DEPLOYMENT") == "1":
        # Replit deployment - use the Replit domain
        return f"https://{os.environ.get('REPLIT_DOMAINS', '').split(',')[0]}"
    elif os.environ.get("RAILWAY_ENVIRONMENT"):
        # Railway deployment
        return os.environ.get("APP_DOMAIN", "https://your-app-domain.com")
    else:
        # Local development - use localhost
        return "http://localhost:5000"

# Set up a persistent folder for PDFs in deployment
is_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT"))

if os.environ.get("REPLIT_DEPLOYMENT") == "1":
    # Replit deployment path
    UPLOAD_FOLDER = '/home/runner/appdata/generated_pdfs'
elif is_railway:
    # Railway deployment - use a volume or consistent storage path
    UPLOAD_FOLDER = os.environ.get("PDF_STORAGE_PATH", '/app/generated_pdfs')
else:
    # Local development
    UPLOAD_FOLDER = 'generated_pdfs'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.logger.info(f"Using persistent storage path: {UPLOAD_FOLDER}")
app.logger.info(f"Deployment mode: {'Railway' if is_railway else ('Replit' if os.environ.get('REPLIT_DEPLOYMENT') == '1' else 'Local')}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bills', methods=['GET'])
def bills():
    try:
        # Get search parameter
        search_query = request.args.get('search', '')
        
        # Try to get bills from SQLite first
        if search_query:
            # Filter bills by client name if search query is provided
            all_bills = Bill.query.filter(Bill.client_name.ilike(f'%{search_query}%')).order_by(Bill.date.desc()).all()
        else:
            # Get all bills if no search query
            all_bills = Bill.query.order_by(Bill.date.desc()).all()
        
        # If no bills in SQLite, try getting from Replit DB
        if len(all_bills) == 0 and not search_query:
            from utils.db_backup import get_all_bills_from_replit_db
            replit_bills = get_all_bills_from_replit_db()
            
            # If we have bills in Replit DB, convert them to Bill objects for display
            if replit_bills:
                for bill_data in replit_bills:
                    new_bill = Bill(
                        bill_number=bill_data['bill_number'],
                        client_name=bill_data['client_name'],
                        phone_number=bill_data['phone_number'],
                        date=bill_data['date'],
                        items=bill_data['items'],
                        subtotal=bill_data['subtotal'],
                        total=bill_data['total'],
                        pdf_path=bill_data['pdf_path'],
                        amount_paid=bill_data['amount_paid'],
                        payment_status=bill_data['payment_status']
                    )
                    db.session.add(new_bill)
                try:
                    db.session.commit()
                    # Fetch the bills again after restoration
                    all_bills = Bill.query.order_by(Bill.date.desc()).all()
                    app.logger.info(f"Restored {len(replit_bills)} bills from Replit DB to SQLite")
                    flash('Bills have been restored from backup and are now permanently saved.', 'success')
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error restoring bills from Replit DB: {str(e)}")
        
        # Add environment variable to ensure database is always preserved
        if os.environ.get("PRESERVE_DB") != "1":
            os.environ["PRESERVE_DB"] = "1"
        
        # Generate QR codes for each bill
        qr_codes = {}
        base_url = get_app_domain()
        from utils.qrcode_generator import generate_bill_qrcode
        
        for bill in all_bills:
            if bill.id:
                qr_codes[bill.id] = generate_bill_qrcode(bill.id, base_url)
            
        return render_template('bills.html', bills=all_bills, search_query=search_query, permanent_storage=True, qr_codes=qr_codes)
    except Exception as e:
        app.logger.error(f"Error in bills route: {str(e)}")
        # If all else fails, get bills directly from Replit DB for display
        from utils.db_backup import get_all_bills_from_replit_db
        replit_bills = get_all_bills_from_replit_db()
        return render_template('bills.html', bills=replit_bills)

@app.route('/generate_bill', methods=['POST'])
def generate_bill():
    try:
        data = request.form
        items = []

        for i in range(len(request.form.getlist('item_name[]'))):
            items.append({
                'name': request.form.getlist('item_name[]')[i],
                'unit': request.form.getlist('unit[]')[i],
                'quantity': float(request.form.getlist('quantity[]')[i]),
                'price': float(request.form.getlist('price[]')[i]),
                'amount': float(request.form.getlist('amount[]')[i])
            })

        bill_number = f"FAB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        # Include client name in the PDF filename
        client_name = data['client_name'].replace(' ', '_')  # Replace spaces with underscores
        # Remove any special characters that might cause issues in filenames
        client_name = ''.join(c for c in client_name if c.isalnum() or c == '_')
        pdf_filename = f"{client_name}_{bill_number}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)

        total = float(data['total'])
        amount_paid = float(data['amount_paid'])

        # Determine payment status
        payment_status = 'pending'
        if amount_paid >= total:
            payment_status = 'paid'
        elif amount_paid > 0:
            payment_status = 'partial'

        # Parse the date from the form
        bill_date = datetime.strptime(data['bill_date'], '%Y-%m-%d') if data.get('bill_date') else datetime.utcnow()
        
        new_bill = Bill(
            bill_number=bill_number,
            client_name=data['client_name'],
            phone_number=data['phone_number'],
            date=bill_date,
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
        
        # Backup to Replit DB
        from utils.db_backup import backup_bill_to_replit_db
        backup_bill_to_replit_db(new_bill)

        flash('Bill generated successfully!', 'success')
        return redirect(url_for('bills'))

    except Exception as e:
        app.logger.error(f"Error generating bill: {str(e)}")
        flash('Error generating bill. Please try again.', 'danger')
        return redirect(url_for('index'))

@app.route('/download_pdf/<int:bill_id>')
def download_pdf(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    
    # Always regenerate the PDF to ensure it has the latest payment information
    # This ensures the PDF shows the most up-to-date payment history
    try:
        # Generate the PDF with the same filename to override the existing one
        pdf_filename = f"{bill.client_name.replace(' ', '_')}_{bill.bill_number}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        generate_pdf(bill, pdf_path)
        app.logger.info(f"Regenerated PDF for bill {bill.bill_number} before download")
    except Exception as e:
        app.logger.error(f"Error regenerating PDF before download: {str(e)}")
        # Continue with download even if regeneration fails
    
    return send_file(bill.pdf_path, as_attachment=True)

@app.route('/view_bill/<int:bill_id>')
def view_bill(bill_id):
    """
    Public facing route to view a bill using a QR code
    This route doesn't require authentication and shows limited bill information
    """
    try:
        bill = Bill.query.get_or_404(bill_id)
        
        # Get payment records for this bill
        from models import PaymentHistory
        
        # Filter by both bill_id and bill_number to ensure we get all relevant payment records
        payment_records = PaymentHistory.query.filter(
            (PaymentHistory.bill_id == bill.id) | 
            ((PaymentHistory.bill_id == None) & (PaymentHistory.bill_number == bill.bill_number))
        ).filter_by(deleted=False).order_by(PaymentHistory.payment_date).all()
        
        # For QR code scanning, we don't need to check for authentication
        return render_template('view_bill.html', bill=bill, payment_records=payment_records)
    except Exception as e:
        app.logger.error(f"Error viewing bill via QR code: {str(e)}")
        return render_template('error.html', message="Could not load the requested bill.")

@app.route('/edit_payment/<int:bill_id>')
def edit_payment(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return render_template('edit_payment.html', bill=bill)

@app.route('/update_payment/<int:bill_id>', methods=['POST'])
def update_payment(bill_id):
    try:
        bill = Bill.query.get_or_404(bill_id)
        
        # If bill is already fully paid, don't allow additional payments
        if bill.payment_status == 'paid':
            flash('This bill is already fully paid.', 'info')
            return redirect(url_for('bills'))
            
        # Get and validate the new payment amount
        try:
            new_payment = float(request.form['new_payment'])
        except ValueError:
            flash('Invalid payment amount. Please enter a valid number.', 'danger')
            return redirect(url_for('edit_payment', bill_id=bill.id))

        # Calculate the pending amount
        pending_amount = bill.total - bill.amount_paid
        
        # Validate payment amount (ensure it's positive and not greater than the pending amount)
        if new_payment <= 0:
            flash('Payment amount must be greater than zero.', 'danger')
            return redirect(url_for('edit_payment', bill_id=bill.id))
            
        if new_payment > pending_amount:
            # Adjust payment to match the pending amount (to prevent overpayment)
            new_payment = pending_amount
            flash('Payment amount adjusted to match the pending amount.', 'warning')

        # Update payment information
        previous_status = bill.payment_status
        bill.amount_paid += new_payment

        # Update payment status based on new total
        if abs(bill.amount_paid - bill.total) < 0.01:  # Using a small epsilon to handle floating point precision
            bill.payment_status = 'paid'
            bill.amount_paid = bill.total  # Ensure exact match to avoid floating point issues
        else:
            bill.payment_status = 'partial'

        # Record this payment in payment history
        from models import PaymentHistory
        payment_record = PaymentHistory(
            bill_id=bill.id,
            bill_number=bill.bill_number,
            client_name=bill.client_name,
            payment_date=datetime.utcnow(),
            amount=new_payment
        )
        db.session.add(payment_record)
        
        # Commit the database changes
        db.session.commit()

        # Backup updated bill to Replit DB
        from utils.db_backup import backup_bill_to_replit_db
        backup_bill_to_replit_db(bill)

        # Create a status message
        status_message = ''
        if bill.payment_status == 'paid' and previous_status != 'paid':
            status_message = 'Bill has been marked as fully paid!'
        elif bill.payment_status == 'partial':
            remaining = bill.total - bill.amount_paid
            status_message = f'Remaining balance: ₹{remaining:.2f}'

        # Update PDF filename with client name
        old_pdf_path = bill.pdf_path
        
        # Remove the old PDF file if it exists
        if os.path.exists(old_pdf_path):
            try:
                os.remove(old_pdf_path)
            except Exception as e:
                app.logger.error(f"Error removing old PDF: {str(e)}")
            
        # Create updated PDF filename with client name
        client_name = bill.client_name.replace(' ', '_')
        client_name = ''.join(c for c in client_name if c.isalnum() or c == '_')
        pdf_filename = f"{client_name}_{bill.bill_number}.pdf"
        new_pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        # Update the bill's PDF path
        bill.pdf_path = new_pdf_path
        
        # Generate updated PDF
        generate_pdf(bill, new_pdf_path)

        # Create success message
        flash(f'Payment of ₹{new_payment:.2f} recorded successfully! {status_message}', 'success')
        return redirect(url_for('bills'))

    except Exception as e:
        app.logger.error(f"Error updating payment: {str(e)}")
        db.session.rollback()
        flash('Error updating payment. Please try again.', 'danger')
        return redirect(url_for('edit_payment', bill_id=bill_id))

@app.route('/edit_bill/<int:bill_id>')
def edit_bill(bill_id):
    try:
        bill = Bill.query.get_or_404(bill_id)
        
        # Only allow editing of pending or partial payments
        if bill.payment_status == 'paid':
            flash('Paid bills cannot be edited.', 'danger')
            return redirect(url_for('bills'))
            
        return render_template('edit_bill.html', bill=bill)
    except Exception as e:
        app.logger.error(f"Error in edit_bill route: {str(e)}")
        flash('Error loading bill. Please try again.', 'danger')
        return redirect(url_for('bills'))

@app.route('/update_bill/<int:bill_id>', methods=['POST'])
def update_bill(bill_id):
    try:
        bill = Bill.query.get_or_404(bill_id)
        
        # Only allow editing of pending or partial payments
        if bill.payment_status == 'paid':
            flash('Paid bills cannot be edited.', 'danger')
            return redirect(url_for('bills'))
            
        data = request.form
        items = []

        for i in range(len(request.form.getlist('item_name[]'))):
            items.append({
                'name': request.form.getlist('item_name[]')[i],
                'unit': request.form.getlist('unit[]')[i],
                'quantity': float(request.form.getlist('quantity[]')[i]),
                'price': float(request.form.getlist('price[]')[i]),
                'amount': float(request.form.getlist('amount[]')[i])
            })

        # Update bill details
        bill.client_name = data['client_name']
        bill.phone_number = data['phone_number']
        
        # Parse the date from the form
        if data.get('bill_date'):
            bill_date = datetime.strptime(data['bill_date'], '%Y-%m-%d')
            bill.date = bill_date
            
        bill.items = items
        bill.subtotal = float(data['subtotal'])
        new_total = float(data['total'])
        
        # Handle the case where total changes but payment was made
        if bill.amount_paid > 0:
            if new_total < bill.amount_paid:
                # If new total is less than amount already paid
                bill.amount_paid = new_total
                bill.payment_status = 'paid'
            else:
                # Recalculate payment status based on new total
                if bill.amount_paid >= new_total:
                    bill.payment_status = 'paid'
                else:
                    bill.payment_status = 'partial'
        
        bill.total = new_total

        # Update PDF filename with client name
        old_pdf_path = bill.pdf_path
        
        # Remove the old PDF file if it exists
        if os.path.exists(old_pdf_path):
            os.remove(old_pdf_path)
            
        # Create updated PDF filename with client name
        client_name = bill.client_name.replace(' ', '_')
        client_name = ''.join(c for c in client_name if c.isalnum() or c == '_')
        pdf_filename = f"{client_name}_{bill.bill_number}.pdf"
        new_pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        # Update the bill's PDF path
        bill.pdf_path = new_pdf_path
        
        # Generate updated PDF
        generate_pdf(bill, new_pdf_path)

        db.session.commit()
        
        # Backup updated bill to Replit DB
        from utils.db_backup import backup_bill_to_replit_db
        backup_bill_to_replit_db(bill)

        flash('Bill updated successfully!', 'success')
        return redirect(url_for('bills'))

    except Exception as e:
        app.logger.error(f"Error updating bill: {str(e)}")
        db.session.rollback()
        flash('Error updating bill. Please try again.', 'danger')
        return redirect(url_for('edit_bill', bill_id=bill_id))

@app.route('/delete_bill/<int:bill_id>', methods=['POST'])
def delete_bill(bill_id):
    try:
        bill = Bill.query.get_or_404(bill_id)

        # Only allow deletion of paid bills
        if bill.payment_status != 'paid':
            flash('Only fully paid bills can be deleted.', 'danger')
            return redirect(url_for('bills'))

        # Delete the PDF file if it exists
        if os.path.exists(bill.pdf_path):
            os.remove(bill.pdf_path)

        # Get the bill info for updating payment history records
        bill_number = bill.bill_number
        bill_id_to_delete = bill.id

        # Delete the bill from database first to release foreign key constraint
        db.session.delete(bill)
        db.session.commit()
        
        # Now handle payment history records separately
        try:
            from models import PaymentHistory
            import sqlalchemy.exc
            
            # After the bill is deleted, update the payment history records
            # Use direct SQL to update records since the model constraint doesn't allow NULL
            # but we've fixed the schema to allow it
            payment_records = PaymentHistory.query.filter_by(bill_id=bill_id_to_delete).all()
            
            for record in payment_records:
                record.bill_id = None
                
            # Commit these changes separately
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.error(f"Error updating payment history records: {str(e)}")
            # Continue with the function even if setting NULL fails
            # The bill is already deleted at this point
        
        # Remove from Replit DB as well
        from utils.db_backup import delete_bill_from_replit_db
        delete_bill_from_replit_db(bill_number)

        flash('Bill deleted successfully! Payment history records have been preserved.', 'success')
        return redirect(url_for('bills'))

    except Exception as e:
        app.logger.error(f"Error deleting bill: {str(e)}")
        db.session.rollback()
        flash('Error deleting bill. Please try again.', 'danger')
        return redirect(url_for('bills'))

@app.route('/payment_history')
def payment_history():
    try:
        # Create a model to track payments with date
        from models import PaymentHistory
        from sqlalchemy.exc import OperationalError
        
        # Get the month filter if provided
        month = request.args.get('month', '')
        
        # Try to filter by deleted=False, but handle the case where the column doesn't exist yet
        try:
            # Only include non-deleted records if the column exists
            base_query = PaymentHistory.query.filter_by(deleted=False)
            
            # First check if any payment records exist
            if month:
                # Filter by selected month (format: YYYY-MM)
                year, month_num = month.split('-')
                payment_records = base_query.filter(
                    db.extract('year', PaymentHistory.payment_date) == int(year),
                    db.extract('month', PaymentHistory.payment_date) == int(month_num)
                ).order_by(PaymentHistory.payment_date.desc()).all()
            else:
                # Get all payments
                payment_records = base_query.order_by(PaymentHistory.payment_date.desc()).all()
                
            # Get list of all months with payments for the dropdown (only include non-deleted records if possible)
            all_months = db.session.query(
                db.extract('year', PaymentHistory.payment_date).label('year'),
                db.extract('month', PaymentHistory.payment_date).label('month')
            ).filter_by(deleted=False).distinct().order_by('year', 'month').all()
            
        except OperationalError as e:
            # If the column doesn't exist, just get all records without filtering
            app.logger.warning("The 'deleted' column doesn't exist yet. Getting all records.")
            
            # Get all records without filtering by deleted
            base_query = PaymentHistory.query
            
            if month:
                # Filter by selected month (format: YYYY-MM)
                year, month_num = month.split('-')
                payment_records = base_query.filter(
                    db.extract('year', PaymentHistory.payment_date) == int(year),
                    db.extract('month', PaymentHistory.payment_date) == int(month_num)
                ).order_by(PaymentHistory.payment_date.desc()).all()
            else:
                # Get all payments
                payment_records = base_query.order_by(PaymentHistory.payment_date.desc()).all()
                
            # Get list of all months without filtering by deleted
            all_months = db.session.query(
                db.extract('year', PaymentHistory.payment_date).label('year'),
                db.extract('month', PaymentHistory.payment_date).label('month')
            ).distinct().order_by('year', 'month').all()
            
            # Add the deleted column to the table - this will be done through the models when the app restarts
            # but we need to handle the current request gracefully
        
        # If no records but we have bills with payments, create payment history records
        if len(payment_records) == 0 and not month:
            bills_with_payments = Bill.query.filter(Bill.amount_paid > 0).all()
            for bill in bills_with_payments:
                # For existing bills, assume payment was made on the bill date
                new_payment = PaymentHistory(
                    bill_id=bill.id,
                    bill_number=bill.bill_number,
                    client_name=bill.client_name,
                    payment_date=bill.date,
                    amount=bill.amount_paid
                )
                db.session.add(new_payment)
            
            try:
                db.session.commit()
                # Refresh payment records
                payment_records = base_query.order_by(PaymentHistory.payment_date.desc()).all()
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error creating payment history: {str(e)}")
        
        # Group payments by client name
        clients = {}
        for record in payment_records:
            if record.client_name not in clients:
                clients[record.client_name] = []
            clients[record.client_name].append(record)
        
        months_list = []
        for year_month in all_months:
            year = int(year_month.year)
            month_num = int(year_month.month)
            month_name = datetime(year, month_num, 1).strftime("%B")
            months_list.append({
                'value': f"{year}-{month_num:02d}",
                'label': f"{month_name} {year}"
            })
            
        return render_template('payment_history.html', 
                              payment_records=payment_records, 
                              clients=clients,
                              months=months_list,
                              selected_month=month)
        
    except Exception as e:
        app.logger.error(f"Error in payment_history route: {str(e)}")
        flash('Error loading payment history. Please try again.', 'danger')
        return redirect(url_for('bills'))

@app.route('/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    try:
        # Get the payment record
        from models import PaymentHistory
        from sqlalchemy.exc import OperationalError
        payment = PaymentHistory.query.get_or_404(payment_id)
        
        try:
            # Try to mark as deleted - this will work if the column exists
            payment.deleted = True
            db.session.commit()
            flash('Payment record has been deleted successfully.', 'success')
        except OperationalError as e:
            # If the column doesn't exist, do a hard delete for now
            app.logger.warning("The 'deleted' column doesn't exist yet. Doing hard delete.")
            db.session.delete(payment)
            db.session.commit()
            flash('Payment record has been permanently deleted.', 'success')
        
        return redirect(url_for('payment_history'))
    
    except Exception as e:
        app.logger.error(f"Error deleting payment record: {str(e)}")
        db.session.rollback()
        flash('Error deleting payment record. Please try again.', 'danger')
        return redirect(url_for('payment_history'))