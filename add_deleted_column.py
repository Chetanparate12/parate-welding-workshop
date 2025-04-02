import sqlite3
import os

def add_deleted_column():
    """Add the 'deleted' column to the payment_history table if it doesn't exist"""
    # Connect to the database
    db_path = 'instance/parate_welding.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the column exists
    cursor.execute("PRAGMA table_info(payment_history)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # Add the column if it doesn't exist
    if 'deleted' not in columns:
        print("Adding 'deleted' column to payment_history table...")
        cursor.execute("ALTER TABLE payment_history ADD COLUMN deleted BOOLEAN DEFAULT 0")
        conn.commit()
        print("Column added successfully.")
    else:
        print("The 'deleted' column already exists in the payment_history table.")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    add_deleted_column()