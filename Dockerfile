FROM python:3.11-slim

WORKDIR /app

# Copy application code first to access railway_requirements.txt
COPY . .

# Install dependencies (using the railway_requirements.txt file)
RUN pip install --no-cache-dir -r railway_requirements.txt

# Create directories for PDF storage and database
RUN mkdir -p generated_pdfs
RUN mkdir -p instance

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV RAILWAY_ENVIRONMENT=1

# Expose the port
EXPOSE $PORT

# Command to run the application
CMD gunicorn main:app --bind 0.0.0.0:$PORT