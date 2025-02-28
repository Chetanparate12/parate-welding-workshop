
import os
import shutil
from flask_frozen import Freezer
from app import app
from models import Bill

# Configure Freezer
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = 'build'
freezer = Freezer(app)

# Add URL generators for dynamic routes
@freezer.register_generator
def bills():
    yield {}  # Main bills page

@freezer.register_generator
def download_pdf():
    with app.app_context():
        for bill in Bill.query.all():
            yield {'bill_id': bill.id}

@freezer.register_generator
def edit_payment():
    with app.app_context():
        for bill in Bill.query.all():
            yield {'bill_id': bill.id}

if __name__ == '__main__':
    # Clean build directory
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Create necessary directories
    os.makedirs('build/generated_pdfs', exist_ok=True)
    os.makedirs('build/static/js', exist_ok=True)
    
    # Copy static files
    if os.path.exists('static'):
        for root, dirs, files in os.walk('static'):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, 'static')
                dst_path = os.path.join('build/static', rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy(src_path, dst_path)
    
    # Copy PDFs to build directory
    pdf_dir = 'generated_pdfs'
    if os.path.exists(pdf_dir):
        for filename in os.listdir(pdf_dir):
            if filename.endswith('.pdf'):
                shutil.copy(os.path.join(pdf_dir, filename), 
                            os.path.join('build/generated_pdfs', filename))
    
    # Generate static files
    with app.app_context():
        freezer.freeze()
    
    print("Static site generated in 'build' directory")
    print("NOTE: This is a read-only version of your site. Interactive features won't work.")
