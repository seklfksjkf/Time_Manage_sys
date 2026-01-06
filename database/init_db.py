"""
Database Initialization Script
Creates all tables for the Time Management System
"""
import pymysql
from config import DatabaseConfig
import sys


class DatabaseInitializer:
    """Database initialization class"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.connection = None
        self.cursor = None
    
    def connect_without_db(self):
        """Connect to MySQL server without selecting a database"""
        try:
            self.connection = pymysql.connect(**self.config.get_connection_params())
            self.cursor = self.connection.cursor()
            print("✓ Successfully connected to MySQL server")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to MySQL server: {e}")
            return False
    
    def connect_with_db(self):
        """Connect to MySQL server with database selected"""
        try:
            self.connection = pymysql.connect(**self.config.get_database_uri())
            self.cursor = self.connection.cursor()
            print(f"✓ Successfully connected to database '{self.config.DB_NAME}'")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to database: {e}")
            return False
    
    def create_database(self):
        """Create the database if it doesn't exist"""
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✓ Database '{self.config.DB_NAME}' created or already exists")
            return True
        except Exception as e:
            print(f"✗ Failed to create database: {e}")
            return False
    
    def create_tables(self):
        """Create all tables"""
        
        tables = {
            'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    avatar VARCHAR(255),
                    role ENUM('admin', 'manager', 'team_member') DEFAULT 'team_member',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    INDEX idx_email (email),
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'projects': """
                CREATE TABLE IF NOT EXISTS projects (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    owner_id INT NOT NULL,
                    start_date DATE,
                    end_date DATE,
                    deadline DATE,
                    status ENUM('planning', 'in_progress', 'completed', 'on_hold', 'cancelled') DEFAULT 'planning',
                    color VARCHAR(7) DEFAULT '#3498db',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_owner (owner_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'tasks': """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    project_id INT NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    estimated_duration INT COMMENT 'in days',
                    actual_duration INT COMMENT 'in days',
                    progress INT DEFAULT 0 COMMENT '0-100',
                    status ENUM('pending', 'in_progress', 'completed', 'blocked') DEFAULT 'pending',
                    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
                    color VARCHAR(7),
                    assigned_to INT,
                    created_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_project (project_id),
                    INDEX idx_status (status),
                    INDEX idx_assigned (assigned_to),
                    INDEX idx_dates (start_date, end_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'task_dependencies': """
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    task_id INT NOT NULL,
                    depends_on_task_id INT NOT NULL,
                    dependency_type ENUM('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish') DEFAULT 'finish_to_start',
                    lag_days INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_dependency (task_id, depends_on_task_id),
                    INDEX idx_task (task_id),
                    INDEX idx_depends_on (depends_on_task_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'milestones': """
                CREATE TABLE IF NOT EXISTS milestones (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    project_id INT NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    date DATE NOT NULL,
                    status ENUM('upcoming', 'completed', 'missed') DEFAULT 'upcoming',
                    color VARCHAR(7) DEFAULT '#e74c3c',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    INDEX idx_project (project_id),
                    INDEX idx_date (date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'project_members': """
                CREATE TABLE IF NOT EXISTS project_members (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    project_id INT NOT NULL,
                    user_id INT NOT NULL,
                    role ENUM('owner', 'manager', 'member', 'viewer') DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_member (project_id, user_id),
                    INDEX idx_project (project_id),
                    INDEX idx_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'version_history': """
                CREATE TABLE IF NOT EXISTS version_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    entity_type ENUM('project', 'task', 'milestone') NOT NULL,
                    entity_id INT NOT NULL,
                    action ENUM('created', 'updated', 'deleted') NOT NULL,
                    changes JSON,
                    changed_by INT NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_entity (entity_type, entity_id),
                    INDEX idx_changed_at (changed_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'task_comments': """
                CREATE TABLE IF NOT EXISTS task_comments (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    task_id INT NOT NULL,
                    user_id INT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_task (task_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'notifications': """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    type ENUM('deadline_alert', 'task_assigned', 'project_update', 'milestone_reached') NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    message TEXT,
                    related_entity_type ENUM('project', 'task', 'milestone'),
                    related_entity_id INT,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_read (user_id, is_read),
                    INDEX idx_created (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'ai_predictions': """
                CREATE TABLE IF NOT EXISTS ai_predictions (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    project_id INT NOT NULL,
                    prediction_type ENUM('duration_estimate', 'deadline_risk', 'success_probability', 'resource_suggestion') NOT NULL,
                    prediction_data JSON NOT NULL,
                    confidence_score DECIMAL(3,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    INDEX idx_project_type (project_id, prediction_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'export_history': """
                CREATE TABLE IF NOT EXISTS export_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    project_id INT NOT NULL,
                    user_id INT NOT NULL,
                    export_type ENUM('pdf', 'png', 'excel') NOT NULL,
                    file_path VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_project (project_id),
                    INDEX idx_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        }
        
        print("\n" + "="*60)
        print("Creating tables...")
        print("="*60)
        
        for table_name, create_sql in tables.items():
            try:
                self.cursor.execute(create_sql)
                print(f"✓ Table '{table_name}' created successfully")
            except Exception as e:
                print(f"✗ Failed to create table '{table_name}': {e}")
                return False
        
        self.connection.commit()
        return True
    
    def insert_sample_data(self):
        """Insert sample data for testing"""
        print("\n" + "="*60)
        print("Inserting sample data...")
        print("="*60)
        
        try:
            # Insert admin user (password: admin123)
            from werkzeug.security import generate_password_hash
            admin_password = generate_password_hash('admin123')
            
            self.cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role)
                VALUES ('admin', 'admin@timemanage.com', %s, 'System Administrator', 'admin')
            """, (admin_password,))
            
            admin_id = self.cursor.lastrowid
            print(f"✓ Created admin user (ID: {admin_id}) - username: admin, password: admin123")
            
            # Insert sample project
            self.cursor.execute("""
                INSERT INTO projects (name, description, owner_id, start_date, end_date, deadline, status)
                VALUES ('Sample Project', 'This is a sample project for testing', %s, '2025-01-01', '2025-12-31', '2025-12-31', 'planning')
            """, (admin_id,))
            
            project_id = self.cursor.lastrowid
            print(f"✓ Created sample project (ID: {project_id})")
            
            # Insert sample task
            self.cursor.execute("""
                INSERT INTO tasks (project_id, title, description, start_date, end_date, status, priority, created_by, assigned_to)
                VALUES (%s, 'Setup Development Environment', 'Install and configure all necessary tools', '2025-01-01', '2025-01-05', 'pending', 'high', %s, %s)
            """, (project_id, admin_id, admin_id))
            
            task_id = self.cursor.lastrowid
            print(f"✓ Created sample task (ID: {task_id})")
            
            # Insert sample milestone
            self.cursor.execute("""
                INSERT INTO milestones (project_id, name, description, date, status)
                VALUES (%s, 'Project Kickoff', 'Project officially starts', '2025-01-01', 'upcoming')
            """, (project_id,))
            
            milestone_id = self.cursor.lastrowid
            print(f"✓ Created sample milestone (ID: {milestone_id})")
            
            self.connection.commit()
            print("\n✓ Sample data inserted successfully!")
            return True
            
        except Exception as e:
            print(f"✗ Failed to insert sample data: {e}")
            return False
    
    def verify_tables(self):
        """Verify that all tables were created"""
        print("\n" + "="*60)
        print("Verifying tables...")
        print("="*60)
        
        try:
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            
            if tables:
                print(f"\nTotal tables created: {len(tables)}")
                for table in tables:
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = self.cursor.fetchone()[0]
                    print(f"  - {table[0]}: {count} records")
                return True
            else:
                print("✗ No tables found!")
                return False
                
        except Exception as e:
            print(f"✗ Failed to verify tables: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("\n✓ Database connection closed")
    
    def initialize(self, with_sample_data=True):
        """Main initialization method"""
        print("="*60)
        print("TIME MANAGEMENT SYSTEM - DATABASE INITIALIZATION")
        print("="*60)
        
        # Step 1: Connect to MySQL server
        if not self.connect_without_db():
            self.close()
            return False
        
        # Step 2: Create database
        if not self.create_database():
            self.close()
            return False
        
        # Close first connection
        self.close()
        
        # Step 3: Connect to the created database
        if not self.connect_with_db():
            return False
        
        # Step 4: Create tables
        if not self.create_tables():
            self.close()
            return False
        
        # Step 5: Insert sample data (optional)
        if with_sample_data:
            if not self.insert_sample_data():
                print("\nWarning: Failed to insert sample data, but tables were created successfully")
        
        # Step 6: Verify tables
        self.verify_tables()
        
        # Close connection
        self.close()
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYou can now start the Flask application.")
        print(f"Database: {self.config.DB_NAME}")
        print(f"Host: {self.config.DB_HOST}:{self.config.DB_PORT}")
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Time Management System Database')
    parser.add_argument('--no-sample-data', action='store_true', 
                       help='Skip inserting sample data')
    
    args = parser.parse_args()
    
    initializer = DatabaseInitializer()
    
    try:
        success = initializer.initialize(with_sample_data=not args.no_sample_data)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Initialization cancelled by user")
        initializer.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        initializer.close()
        sys.exit(1)


if __name__ == "__main__":
    main()

