"""
Migration script to add task_assignments table for multiple assignees support
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.config import DatabaseConfig
import pymysql


def migrate():
    """Add task_assignments table"""
    config = DatabaseConfig()

    try:
        # Connect to database
        connection = pymysql.connect(**config.get_database_uri())
        cursor = connection.cursor()

        # Check if table already exists
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema = DATABASE() AND table_name = 'task_assignments'
        """)
        result = cursor.fetchone()

        if result[0] > 0:
            print("✓ task_assignments table already exists")
            return True

        # Create task_assignments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_assignments (
                id INT PRIMARY KEY AUTO_INCREMENT,
                task_id INT NOT NULL,
                user_id INT NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_by INT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL,
                UNIQUE KEY unique_task_assignment (task_id, user_id),
                INDEX idx_task (task_id),
                INDEX idx_user (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        connection.commit()
        print("✓ task_assignments table created successfully")

        # Migrate existing single assignees to task_assignments
        cursor.execute("""
            INSERT INTO task_assignments (task_id, user_id, assigned_by)
            SELECT id, assigned_to, created_by
            FROM tasks
            WHERE assigned_to IS NOT NULL
        """)

        connection.commit()
        migrated_count = cursor.rowcount
        print(f"✓ Migrated {migrated_count} existing task assignments")

        cursor.close()
        connection.close()
        print("\n✓ Migration completed successfully!")
        print("  You can now assign multiple people to tasks.")
        return True

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False


if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
