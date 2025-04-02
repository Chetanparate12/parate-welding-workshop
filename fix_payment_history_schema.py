import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_payment_history_schema():
    """
    Fix the payment_history table schema to allow NULL values in bill_id column
    This is necessary for the delete_bill functionality to work properly
    """
    try:
        # Determine the database path based on deployment environment
        if os.environ.get("REPLIT_DEPLOYMENT") == "1":
            db_path = "/home/runner/appdata/bills.db"
        elif os.environ.get("RAILWAY_ENVIRONMENT"):
            # On Railway, PostgreSQL is used, so this script isn't applicable
            logger.info("Running on Railway with PostgreSQL - this fix is not needed")
            return
        else:
            db_path = "instance/bills.db"
        
        # Check if the database file exists
        if not os.path.exists(db_path):
            logger.warning(f"Database file not found at {db_path}")
            return
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the payment_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_history'")
        if not cursor.fetchone():
            logger.warning("payment_history table does not exist")
            conn.close()
            return
        
        # Get current schema info
        cursor.execute("PRAGMA table_info(payment_history)")
        columns = cursor.fetchall()
        bill_id_info = next((col for col in columns if col[1] == 'bill_id'), None)
        
        if not bill_id_info:
            logger.warning("bill_id column not found in payment_history table")
            conn.close()
            return
        
        # Check if bill_id column already allows NULL
        nullable = bill_id_info[3] == 0  # SQLite schema: notnull is 1 if NOT NULL, 0 if nullable
        if nullable:
            logger.info("bill_id column already allows NULL values")
            conn.close()
            return
        
        # We need to recreate the table to change the NULL constraint
        # First, get all column definitions
        columns_def = []
        for col in columns:
            name = col[1]
            type_name = col[2]
            not_null = "NOT NULL" if col[3] == 1 and name != 'bill_id' else ""
            default = f"DEFAULT {col[4]}" if col[4] is not None else ""
            pk = "PRIMARY KEY" if col[5] == 1 else ""
            columns_def.append(f"{name} {type_name} {pk} {not_null} {default}".strip())
        
        # Create a new table with the correct schema
        cursor.execute("BEGIN TRANSACTION")
        
        # Create temporary table
        cursor.execute(f"""
        CREATE TABLE payment_history_new (
            {', '.join(columns_def)}
        )
        """)
        
        # Copy data from old table to new
        cursor.execute("INSERT INTO payment_history_new SELECT * FROM payment_history")
        
        # Drop old table
        cursor.execute("DROP TABLE payment_history")
        
        # Rename new table
        cursor.execute("ALTER TABLE payment_history_new RENAME TO payment_history")
        
        # Commit the transaction
        conn.commit()
        logger.info("Successfully modified payment_history schema to allow NULL bill_id values")
        
        # Close the connection
        conn.close()
    
    except Exception as e:
        logger.error(f"Error fixing payment_history schema: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fix_payment_history_schema()