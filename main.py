from app import app
import sys
import logging

if __name__ == "__main__":
    try:
        # Set up error logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        print("Billing app starting with Replit Auth enabled.")
        print("Access the app and log in with your Replit account.")
        # Run the Flask application
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
