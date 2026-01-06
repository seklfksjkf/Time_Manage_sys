"""
Quick Setup Script
Quickly setup database with password 123456
"""
import os


def create_env_file():
    """Create .env file with default settings"""
    env_content = """# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=time_manage_sys

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production-2025
JWT_SECRET_KEY=jwt-secret-key-change-in-production-2025

# Server Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✓ Created .env file with password: 123456")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False


def main():
    print("="*60)
    print("QUICK SETUP - Time Management System")
    print("="*60)
    print("\nThis will setup the database with:")
    print("  - MySQL Password: 123456")
    print("  - Database Name: time_manage_sys")
    print("  - Sample users and projects")
    print("="*60)
    
    # Create .env file
    if not create_env_file():
        return
    
    print("\n✓ Configuration complete!")
    print("\nNext steps:")
    print("  1. Initialize database:")
    print("     python database/init_db.py")
    print("\n  2. Add more sample data (optional):")
    print("     python database/seed_data.py")
    print("\n  3. Or add sample data and clear existing:")
    print("     python database/seed_data.py --clear")


if __name__ == "__main__":
    main()

