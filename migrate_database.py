import sqlite3
import os
import logging

def migrate_database():
    """
    Perform any necessary database migrations on application startup.
    Currently adding 'deleted' column to payment_history table if it doesn't exist.
    """
    logging.info("Checking for database migrations...")
    
    # Get the database path from the environment or use the default
    db_path = os.path.join('instance', 'bills.db')
    
    # Make sure the database exists
    if not os.path.exists(db_path):
        logging.warning(f"Database file {db_path} not found, skipping migrations.")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the payment_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_history'")
        if not cursor.fetchone():
            logging.warning("payment_history table doesn't exist yet, skipping migrations.")
            return
        
        # Check if the deleted column exists
        cursor.execute("PRAGMA table_info(payment_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add the deleted column if it doesn't exist
        if 'deleted' not in columns:
            logging.info("Adding 'deleted' column to payment_history table...")
            cursor.execute("ALTER TABLE payment_history ADD COLUMN deleted BOOLEAN DEFAULT 0")
            conn.commit()
            logging.info("Successfully added 'deleted' column to payment_history table.")
            
    except Exception as e:
        logging.error(f"Error during database migration: {str(e)}")
    finally:
        # Close the connection
        conn.close()