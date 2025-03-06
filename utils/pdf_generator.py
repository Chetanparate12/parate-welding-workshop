from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from models import PaymentHistory
from app import db

def generate_pdf(bill, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    header_style = ParagraphStyle(
        'CustomHeader',
        fontSize=16,
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph("Parate Welding Workshop", header_style))

    # Bill Info
    elements.append(Paragraph(f"Bill Number: {bill.bill_number}", styles['Normal']))
    elements.append(Paragraph(f"Date: {bill.date.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Client Info
    elements.append(Paragraph("Client Information:", styles['Heading2']))
    elements.append(Paragraph(f"Name: {bill.client_name}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {bill.phone_number}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Items Table
    items_data = [['Item', 'Quantity/Weight', 'Unit', 'Price', 'Amount']]
    for item in bill.items:
        quantity_text = f"{item['quantity']:.2f}"
        if item['unit'] == 'kilogram':
            quantity_text += ' kg'

        items_data.append([
            item['name'],
            quantity_text,
            item['unit'].title(),
            f"₹{item['price']:.2f}",
            f"₹{item['amount']:.2f}"
        ])

    table = Table(items_data, colWidths=[3*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))

    # Payment Information
    elements.append(Paragraph("Payment Information:", styles['Heading2']))
    elements.append(Paragraph(f"Total Amount: ₹{bill.total:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Amount Paid: ₹{bill.amount_paid:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Pending Amount: ₹{(bill.total - bill.amount_paid):.2f}", styles['Normal']))
    elements.append(Paragraph(f"Payment Status: {bill.payment_status.title()}", styles['Normal']))
    
    # Payment History
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Payment History:", styles['Heading2']))
    
    try:
        # Get payment history for this bill
        payment_records = PaymentHistory.query.filter_by(bill_id=bill.id).order_by(PaymentHistory.payment_date).all()
        
        if payment_records:
            # Create payment history table
            payment_data = [['Date', 'Amount']]
            for record in payment_records:
                payment_data.append([
                    record.payment_date.strftime('%Y-%m-%d'),
                    f"₹{record.amount:.2f}"
                ])
            
            payment_table = Table(payment_data, colWidths=[3*inch, 3*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ]))
            elements.append(payment_table)
        else:
            elements.append(Paragraph("No payment records found.", styles['Normal']))
    except Exception as e:
        elements.append(Paragraph("Could not retrieve payment history.", styles['Normal']))

    doc.build(elements)