"""
Database Reset Script
WARNING: This will drop all tables and recreate them
"""
import pymysql
from config import DatabaseConfig
import sys


def reset_database():
    """Drop and recreate the database"""
    config = DatabaseConfig()
    
    print("="*60)
    print("WARNING: DATABASE RESET")
    print("="*60)
    print(f"This will DELETE ALL DATA in database: {config.DB_NAME}")
    print("This action CANNOT be undone!")
    print("="*60)
    
    # Ask for confirmation
    confirmation = input("\nType 'YES' to confirm: ")
    
    if confirmation != 'YES':
        print("✗ Reset cancelled")
        return False
    
    try:
        # Connect to MySQL server
        connection = pymysql.connect(**config.get_connection_params())
        cursor = connection.cursor()
        
        print(f"\n✓ Connected to MySQL server")
        
        # Drop database
        cursor.execute(f"DROP DATABASE IF EXISTS {config.DB_NAME}")
        print(f"✓ Database '{config.DB_NAME}' dropped")
        
        cursor.close()
        connection.close()
        
        print("\n✓ Database reset completed!")
        print("\nNow run 'python database/init_db.py' to recreate the database")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to reset database: {e}")
        return False


if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)

