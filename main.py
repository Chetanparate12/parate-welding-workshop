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
        
        # Get port from environment variable (for Render compatibility)
        port = int(os.environ.get("PORT", 5000))
        
        # Check if we're in deployment mode
        is_deployment = os.environ.get("RENDER") == "1"
        if is_deployment:
            print("Billing app starting in DEPLOYMENT mode - data will be saved permanently")
            debug_mode = False
        else:
            print("Billing app starting in DEVELOPMENT mode - authentication disabled")
            debug_mode = True
            
        # Run the Flask application
        app.run(host="0.0.0.0", port=port, debug=debug_mode)
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        sys.exit(1)
