from app import app

# Add Gunicorn configuration
bind = "0.0.0.0:10000"
workers = 2
timeout = 120

if __name__ == "__main__":
    app.run()