import os
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable, Frame
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Line, Drawing
from models import PaymentHistory
from app import db

class HorizontalLine(Flowable):
    """Custom Flowable for drawing horizontal lines"""
    
    def __init__(self, width, thickness=1, color=colors.black, space_before=0, space_after=0):
        Flowable.__init__(self)
        self.width = width
        self.thickness = thickness
        self.color = color
        self.space_before = space_before
        self.space_after = space_after
        
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 0, self.width, 0)

def generate_pdf(bill, output_path):
    # Use A4 for a professional standard size
    page_width, page_height = A4
    
    # Create a document with appropriate margins
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Get the standard style sheet and define custom styles
    styles = getSampleStyleSheet()
    
    # Custom styles for improved appearance
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=0.5*cm,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        spaceAfter=0.2*cm
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_LEFT,
        textColor=colors.darkblue,
        spaceAfter=0.2*cm
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=0.1*cm
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_RIGHT
    )
    
    # List to hold the PDF elements
    elements = []
    
    # Add a welding-themed logo
    try:
        # Create a simple text-based logo
        elements.append(Paragraph("PARATE WELDING WORKSHOP", title_style))
        elements.append(Paragraph("Professional Metal Fabrication Services", subtitle_style))
        elements.append(HorizontalLine(page_width-3*cm, 2, colors.darkblue, 0.3*cm, 0.5*cm))
    except Exception as e:
        # If logo creation fails, just add text header
        elements.append(Paragraph("PARATE WELDING WORKSHOP", title_style))
    
    # Bill Info section with better layout
    bill_info_data = [
        ['Bill Number:', bill.bill_number, 'Date:', bill.date.strftime('%d %b, %Y')],
    ]
    
    bill_info_table = Table(bill_info_data, colWidths=[2.5*cm, 5*cm, 2*cm, 4*cm])
    bill_info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.darkblue),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(bill_info_table)
    elements.append(Spacer(1, 0.3*cm))
    
    # Client Info with improved presentation
    elements.append(Paragraph("CLIENT INFORMATION", heading_style))
    elements.append(HorizontalLine(8*cm, 1, colors.darkgrey, 0, 0.2*cm))
    
    client_data = [
        ['Client Name:', bill.client_name],
        ['Phone Number:', bill.phone_number]
    ]
    
    client_table = Table(client_data, colWidths=[3*cm, 10*cm])
    client_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONT', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(client_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Items Table with improved styling
    elements.append(Paragraph("ITEMS", heading_style))
    elements.append(HorizontalLine(8*cm, 1, colors.darkgrey, 0, 0.2*cm))
    
    items_data = [['Item Description', 'Quantity/Weight', 'Unit', 'Price (₹)', 'Amount (₹)']]
    
    for item in bill.items:
        quantity_text = f"{item['quantity']:.2f}"
        if item['unit'] == 'kilogram':
            quantity_text += ' kg'
        
        items_data.append([
            item['name'],
            quantity_text,
            item['unit'].title(),
            f"{item['price']:.2f}",
            f"{item['amount']:.2f}"
        ])
    
    # Add a totals row
    items_data.append(['', '', '', 'Total:', f"{bill.total:.2f}"])
    
    # Create table with proper column widths
    items_table = Table(items_data, colWidths=[6*cm, 3*cm, 2*cm, 2.5*cm, 2.5*cm])
    
    # Style the table professionally
    table_style = [
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Item name left aligned
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # All numbers right aligned
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        
        # Alternating row colors for readability
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
        
        # Total row styling
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (-2, -1), (-1, -1), 1, colors.black),
        ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
    ]
    
    items_table.setStyle(TableStyle(table_style))
    elements.append(items_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Payment Information with better layout
    elements.append(Paragraph("PAYMENT DETAILS", heading_style))
    elements.append(HorizontalLine(8*cm, 1, colors.darkgrey, 0, 0.2*cm))
    
    payment_info_data = [
        ['Total Amount:', f"₹{bill.total:.2f}"],
        ['Amount Paid:', f"₹{bill.amount_paid:.2f}"],
        ['Pending Amount:', f"₹{(bill.total - bill.amount_paid):.2f}"],
        ['Payment Status:', bill.payment_status.title()]
    ]
    
    # Highlight the payment status with color
    status_color = colors.green if bill.payment_status == 'paid' else (
        colors.orange if bill.payment_status == 'partial' else colors.red
    )
    
    payment_table = Table(payment_info_data, colWidths=[4*cm, 10*cm])
    payment_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (0, -1), (1, -1), status_color),
    ]))
    
    elements.append(payment_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # Payment History with improved styling
    try:
        payment_records = PaymentHistory.query.filter_by(bill_id=bill.id).order_by(PaymentHistory.payment_date).all()
        
        if payment_records:
            elements.append(Paragraph("PAYMENT HISTORY", heading_style))
            elements.append(HorizontalLine(8*cm, 1, colors.darkgrey, 0, 0.2*cm))
            
            payment_data = [['Date', 'Amount (₹)']]
            for record in payment_records:
                payment_data.append([
                    record.payment_date.strftime('%d %b, %Y'),
                    f"{record.amount:.2f}"
                ])
            
            # Total row
            payment_data.append(['Total Paid:', f"{bill.amount_paid:.2f}"])
            
            payment_table = Table(payment_data, colWidths=[6*cm, 6*cm])
            payment_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Data rows
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                
                # Alternating rows
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
                
                # Total row
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('ALIGN', (0, -1), (0, -1), 'RIGHT'),
            ]))
            
            elements.append(payment_table)
        else:
            elements.append(Paragraph("No payment records found.", normal_style))
    except Exception as e:
        elements.append(Paragraph("Could not retrieve payment history.", normal_style))
    
    # Footer with terms and contact information
    elements.append(Spacer(1, 1*cm))
    elements.append(HorizontalLine(page_width-3*cm, 1, colors.darkblue, 0, 0.3*cm))
    
    footer_text = """
    Thank you for your business! For any questions regarding this invoice, please contact us.
    Terms: Payment is due within 30 days. Late payments may be subject to a fee.
    """
    
    elements.append(Paragraph(footer_text, info_style))
    
    # Build the PDF
    doc.build(elements)