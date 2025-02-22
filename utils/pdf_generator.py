from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

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
    elements.append(Paragraph("Fabrication Bill", header_style))

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
    items_data = [['Item', 'Quantity', 'Price', 'Amount']]
    for item in bill.items:
        items_data.append([
            item['name'],
            str(item['quantity']),
            f"₹{item['price']:.2f}",
            f"₹{item['amount']:.2f}"
        ])

    table = Table(items_data, colWidths=[4*inch, 1*inch, 1*inch, 1*inch])
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

    doc.build(elements)