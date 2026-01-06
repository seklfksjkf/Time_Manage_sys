"""
Database Setup Wizard
Interactive setup script for Time Management System
"""
import os
import sys
from getpass import getpass


def create_env_file():
    """Interactive wizard to create .env file"""
    print("=" * 60)
    print("TIME MANAGEMENT SYSTEM - SETUP WIZARD")
    print("=" * 60)
    print("\nThis wizard will help you configure the database connection.\n")
    
    # Get database configuration
    print("Database Configuration:")
    print("-" * 60)
    
    db_host = input("MySQL Host [localhost]: ").strip() or "localhost"
    db_port = input("MySQL Port [3306]: ").strip() or "3306"
    db_user = input("MySQL Username [root]: ").strip() or "root"
    db_password = getpass("MySQL Password: ").strip()
    db_name = input("Database Name [time_manage_sys]: ").strip() or "time_manage_sys"
    
    print("\nFlask Configuration:")
    print("-" * 60)
    
    flask_env = input("Environment (development/production) [development]: ").strip() or "development"
    
    # Generate secret keys
    import secrets
    secret_key = secrets.token_hex(32)
    jwt_secret_key = secrets.token_hex(32)
    
    print("\n✓ Secret keys generated automatically")
    
    flask_host = input("\nFlask Host [0.0.0.0]: ").strip() or "0.0.0.0"
    flask_port = input("Flask Port [5000]: ").strip() or "5000"
    
    # Create .env content
    env_content = f"""# Database Configuration
DB_HOST={db_host}
DB_PORT={db_port}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_NAME={db_name}

# Flask Configuration
FLASK_ENV={flask_env}
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret_key}

# Server Configuration
FLASK_HOST={flask_host}
FLASK_PORT={flask_port}
"""
    
    # Save .env file
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("\n✓ Configuration saved to .env file")
        return True
    except Exception as e:
        print(f"\n✗ Failed to save .env file: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("Testing Database Connection...")
    print("=" * 60)
    
    try:
        import pymysql
        from database.config import DatabaseConfig
        
        config = DatabaseConfig()
        connection = pymysql.connect(**config.get_connection_params())
        connection.close()
        
        print("✓ Successfully connected to MySQL server!")
        return True
        
    except ImportError:
        print("✗ PyMySQL not installed. Please run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nPlease check your database configuration in .env file")
        return False


def run_initialization():
    """Run database initialization"""
    print("\n" + "=" * 60)
    print("Initialize Database")
    print("=" * 60)
    
    choice = input("\nDo you want to initialize the database now? (y/n): ").lower()
    
    if choice == 'y':
        sample_data = input("Include sample data? (y/n) [y]: ").lower() or 'y'
        
        print("\nInitializing database...\n")
        
        if sample_data == 'y':
            os.system("python database/init_db.py")
        else:
            os.system("python database/init_db.py --no-sample-data")
        
        return True
    else:
        print("\nYou can initialize the database later by running:")
        print("  python database/init_db.py")
        return False


def main():
    """Main setup wizard"""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("Warning: .env file already exists!")
        choice = input("Do you want to overwrite it? (y/n): ").lower()
        if choice != 'y':
            print("Setup cancelled.")
            return
    
    # Step 1: Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_database_connection():
        print("\n✗ Setup incomplete. Please fix the connection issues and try again.")
        sys.exit(1)
    
    # Step 3: Initialize database
    run_initialization()
    
    # Final message
    print("\n" + "=" * 60)
    print("SETUP COMPLETED!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Check the configuration in .env file")
    print("  2. Start the Flask backend: python app.py")
    print("  3. Setup the Vue.js frontend in /frontend directory")
    print("\nDefault admin credentials (if sample data was loaded):")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

