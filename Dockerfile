FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for PDF storage and database
RUN mkdir -p generated_pdfs
RUN mkdir -p instance

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Expose the port
EXPOSE $PORT

# Command to run the application
CMD gunicorn main:app --bind 0.0.0.0:$PORT