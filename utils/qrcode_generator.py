import os
import qrcode
from io import BytesIO
import base64

def generate_qrcode(data, size=10):
    """
    Generate a QR code for the given data
    
    Parameters:
    - data: The data to encode in the QR code (typically a URL)
    - size: The size of the QR code image (default: 10)
    
    Returns:
    - A base64 encoded string of the QR code image that can be embedded in HTML
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code to BytesIO object
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    
    # Get the base64 encoded string
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_bill_qrcode(bill_id, base_url):
    """
    Generate a QR code with a URL to view a specific bill
    
    Parameters:
    - bill_id: The ID of the bill
    - base_url: The base URL of the application
    
    Returns:
    - A base64 encoded string of the QR code image
    """
    # Create URL for the bill view
    url = f"{base_url}/view_bill/{bill_id}"
    
    # Generate QR code
    return generate_qrcode(url)