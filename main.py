from app import app
import sys
import os
import logging

if __name__ == "__main__":
    try:
        # Set up error logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Check if we're in deployment mode
        is_deployment = os.environ.get("REPLIT_DEPLOYMENT") == "1"
        if is_deployment:
            print("Billing app starting in DEPLOYMENT mode - data will be saved permanently")
            # Set debug to False in deployment for security
            debug_mode = False
        else:
            print("Billing app starting in DEVELOPMENT mode - authentication disabled")
            debug_mode = True
            
        # Run the Flask application
        app.run(host="0.0.0.0", port=5000, debug=debug_mode)
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
