
import os
import shutil
from flask_frozen import Freezer
from app import app

# Configure Freezer
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_DESTINATION'] = 'build'
freezer = Freezer(app)

if __name__ == '__main__':
    # Clean build directory
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Ensure PDFs directory exists in build
    os.makedirs('build/generated_pdfs', exist_ok=True)
    
    # Copy PDFs to build directory
    pdf_dir = 'generated_pdfs'
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            shutil.copy(os.path.join(pdf_dir, filename), 
                        os.path.join('build/generated_pdfs', filename))
    
    # Generate static files
    freezer.freeze()
    
    print("Static site generated in 'build' directory")
