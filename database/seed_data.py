"""
Database Seed Script
Creates comprehensive sample data for testing and demonstration
"""
import pymysql
from config import DatabaseConfig
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import sys


class DataSeeder:
    """Data seeding class"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Connect to database"""
        try:
            self.connection = pymysql.connect(**self.config.get_database_uri())
            self.cursor = self.connection.cursor()
            print("✓ Connected to database")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    def clear_existing_data(self):
        """Clear existing data (optional)"""
        print("\n" + "="*60)
        print("Clearing existing data...")
        print("="*60)
        
        try:
            # Disable foreign key checks
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            tables = [
                'export_history', 'ai_predictions', 'notifications',
                'task_comments', 'version_history', 'project_members',
                'milestones', 'task_dependencies', 'tasks', 'projects', 'users'
            ]
            
            for table in tables:
                self.cursor.execute(f"TRUNCATE TABLE {table}")
                print(f"✓ Cleared table: {table}")
            
            # Re-enable foreign key checks
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            print("✓ All data cleared successfully")
            return True
            
        except Exception as e:
            print(f"✗ Failed to clear data: {e}")
            return False
    
    def seed_users(self):
        """Create sample users"""
        print("\n" + "="*60)
        print("Creating users...")
        print("="*60)
        
        users_data = [
            ('admin', 'admin@timemanage.com', 'admin123', 'System Administrator', 'admin'),
            ('john_doe', 'john.doe@company.com', 'password123', 'John Doe', 'manager'),
            ('jane_smith', 'jane.smith@company.com', 'password123', 'Jane Smith', 'manager'),
            ('mike_wilson', 'mike.wilson@company.com', 'password123', 'Mike Wilson', 'team_member'),
            ('sarah_brown', 'sarah.brown@company.com', 'password123', 'Sarah Brown', 'team_member'),
            ('david_lee', 'david.lee@company.com', 'password123', 'David Lee', 'team_member'),
            ('emily_davis', 'emily.davis@company.com', 'password123', 'Emily Davis', 'team_member'),
            ('robert_chen', 'robert.chen@company.com', 'password123', 'Robert Chen', 'team_member'),
        ]
        
        user_ids = {}
        
        for username, email, password, full_name, role in users_data:
            try:
                password_hash = generate_password_hash(password)
                self.cursor.execute("""
                    INSERT INTO users (username, email, password_hash, full_name, role, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (username, email, password_hash, full_name, role))
                
                user_id = self.cursor.lastrowid
                user_ids[username] = user_id
                print(f"✓ Created user: {username} ({full_name}) - Role: {role}")
                
            except Exception as e:
                # If user already exists, get their ID
                if '1062' in str(e) or 'Duplicate' in str(e):
                    print(f"⚠ User {username} already exists, fetching ID...")
                    self.cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    result = self.cursor.fetchone()
                    if result:
                        user_ids[username] = result[0]
                        print(f"✓ Found existing user: {username} (ID: {result[0]})")
                else:
                    print(f"✗ Failed to create user {username}: {e}")
        
        self.connection.commit()
        return user_ids
    
    def seed_projects(self, user_ids):
        """Create sample projects"""
        print("\n" + "="*60)
        print("Creating projects...")
        print("="*60)
        
        today = datetime.now().date()
        
        projects_data = [
            {
                'name': 'Website Redesign Project',
                'description': 'Complete redesign of company website with modern UI/UX',
                'owner': 'john_doe',
                'start_date': today,
                'end_date': today + timedelta(days=90),
                'deadline': today + timedelta(days=90),
                'status': 'in_progress',
                'color': '#3498db'
            },
            {
                'name': 'Mobile App Development',
                'description': 'Native iOS and Android app for customer engagement',
                'owner': 'jane_smith',
                'start_date': today - timedelta(days=30),
                'end_date': today + timedelta(days=120),
                'deadline': today + timedelta(days=120),
                'status': 'in_progress',
                'color': '#2ecc71'
            },
            {
                'name': 'Marketing Campaign Q1 2025',
                'description': 'Comprehensive marketing campaign for product launch',
                'owner': 'john_doe',
                'start_date': today - timedelta(days=10),
                'end_date': today + timedelta(days=80),
                'deadline': today + timedelta(days=80),
                'status': 'in_progress',
                'color': '#e74c3c'
            },
            {
                'name': 'Infrastructure Upgrade',
                'description': 'Server and database infrastructure modernization',
                'owner': 'admin',
                'start_date': today,
                'end_date': today + timedelta(days=60),
                'deadline': today + timedelta(days=60),
                'status': 'planning',
                'color': '#f39c12'
            },
            {
                'name': 'Customer Portal v2.0',
                'description': 'Enhanced customer self-service portal',
                'owner': 'jane_smith',
                'start_date': today + timedelta(days=7),
                'end_date': today + timedelta(days=100),
                'deadline': today + timedelta(days=100),
                'status': 'planning',
                'color': '#9b59b6'
            }
        ]
        
        project_ids = []
        
        for project in projects_data:
            try:
                owner_id = user_ids.get(project['owner'])
                self.cursor.execute("""
                    INSERT INTO projects (name, description, owner_id, start_date, end_date, deadline, status, color)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    project['name'], project['description'], owner_id,
                    project['start_date'], project['end_date'], project['deadline'],
                    project['status'], project['color']
                ))
                
                project_id = self.cursor.lastrowid
                project_ids.append({
                    'id': project_id,
                    'name': project['name'],
                    'owner': project['owner']
                })
                print(f"✓ Created project: {project['name']} (ID: {project_id})")
                
            except Exception as e:
                print(f"✗ Failed to create project {project['name']}: {e}")
        
        self.connection.commit()
        return project_ids
    
    def seed_project_members(self, user_ids, project_ids):
        """Assign team members to projects"""
        print("\n" + "="*60)
        print("Assigning project members...")
        print("="*60)
        
        # Project 1: Website Redesign - Full team
        project_1_members = [
            (project_ids[0]['id'], user_ids['john_doe'], 'owner'),
            (project_ids[0]['id'], user_ids['mike_wilson'], 'member'),
            (project_ids[0]['id'], user_ids['sarah_brown'], 'member'),
            (project_ids[0]['id'], user_ids['david_lee'], 'member'),
        ]
        
        # Project 2: Mobile App - Development team
        project_2_members = [
            (project_ids[1]['id'], user_ids['jane_smith'], 'owner'),
            (project_ids[1]['id'], user_ids['emily_davis'], 'member'),
            (project_ids[1]['id'], user_ids['robert_chen'], 'member'),
        ]
        
        # Project 3: Marketing Campaign
        project_3_members = [
            (project_ids[2]['id'], user_ids['john_doe'], 'owner'),
            (project_ids[2]['id'], user_ids['sarah_brown'], 'member'),
        ]
        
        # Project 4: Infrastructure
        project_4_members = [
            (project_ids[3]['id'], user_ids['admin'], 'owner'),
            (project_ids[3]['id'], user_ids['robert_chen'], 'member'),
            (project_ids[3]['id'], user_ids['david_lee'], 'member'),
        ]
        
        # Project 5: Customer Portal
        project_5_members = [
            (project_ids[4]['id'], user_ids['jane_smith'], 'owner'),
            (project_ids[4]['id'], user_ids['mike_wilson'], 'member'),
            (project_ids[4]['id'], user_ids['emily_davis'], 'member'),
        ]
        
        all_members = project_1_members + project_2_members + project_3_members + project_4_members + project_5_members
        
        for project_id, user_id, role in all_members:
            try:
                self.cursor.execute("""
                    INSERT INTO project_members (project_id, user_id, role)
                    VALUES (%s, %s, %s)
                """, (project_id, user_id, role))
                print(f"✓ Added member to project {project_id}")
            except Exception as e:
                print(f"✗ Failed to add member: {e}")
        
        self.connection.commit()
    
    def seed_tasks(self, user_ids, project_ids):
        """Create sample tasks"""
        print("\n" + "="*60)
        print("Creating tasks...")
        print("="*60)
        
        today = datetime.now().date()
        
        # Tasks for Project 1: Website Redesign
        project_1_tasks = [
            {
                'title': 'Requirements Gathering',
                'description': 'Collect and document all requirements from stakeholders',
                'start': today,
                'end': today + timedelta(days=7),
                'status': 'completed',
                'priority': 'high',
                'progress': 100,
                'assigned_to': 'mike_wilson'
            },
            {
                'title': 'UI/UX Design',
                'description': 'Create wireframes and mockups for new design',
                'start': today + timedelta(days=7),
                'end': today + timedelta(days=21),
                'status': 'in_progress',
                'priority': 'high',
                'progress': 65,
                'assigned_to': 'sarah_brown'
            },
            {
                'title': 'Frontend Development',
                'description': 'Implement responsive design using React',
                'start': today + timedelta(days=21),
                'end': today + timedelta(days=50),
                'status': 'pending',
                'priority': 'high',
                'progress': 0,
                'assigned_to': 'david_lee'
            },
            {
                'title': 'Backend API Development',
                'description': 'Build RESTful APIs for frontend integration',
                'start': today + timedelta(days=21),
                'end': today + timedelta(days=50),
                'status': 'pending',
                'priority': 'high',
                'progress': 0,
                'assigned_to': 'mike_wilson'
            },
            {
                'title': 'Content Migration',
                'description': 'Migrate existing content to new platform',
                'start': today + timedelta(days=50),
                'end': today + timedelta(days=65),
                'status': 'pending',
                'priority': 'medium',
                'progress': 0,
                'assigned_to': 'sarah_brown'
            },
            {
                'title': 'Testing and QA',
                'description': 'Comprehensive testing across all browsers and devices',
                'start': today + timedelta(days=65),
                'end': today + timedelta(days=80),
                'status': 'pending',
                'priority': 'critical',
                'progress': 0,
                'assigned_to': 'mike_wilson'
            },
            {
                'title': 'Deployment',
                'description': 'Deploy to production environment',
                'start': today + timedelta(days=80),
                'end': today + timedelta(days=90),
                'status': 'pending',
                'priority': 'critical',
                'progress': 0,
                'assigned_to': 'david_lee'
            }
        ]
        
        # Tasks for Project 2: Mobile App
        project_2_tasks = [
            {
                'title': 'App Architecture Design',
                'description': 'Design overall app architecture and tech stack',
                'start': today - timedelta(days=30),
                'end': today - timedelta(days=20),
                'status': 'completed',
                'priority': 'high',
                'progress': 100,
                'assigned_to': 'emily_davis'
            },
            {
                'title': 'iOS Development',
                'description': 'Build native iOS app using Swift',
                'start': today - timedelta(days=20),
                'end': today + timedelta(days=40),
                'status': 'in_progress',
                'priority': 'high',
                'progress': 45,
                'assigned_to': 'emily_davis'
            },
            {
                'title': 'Android Development',
                'description': 'Build native Android app using Kotlin',
                'start': today - timedelta(days=20),
                'end': today + timedelta(days=40),
                'status': 'in_progress',
                'priority': 'high',
                'progress': 50,
                'assigned_to': 'robert_chen'
            },
            {
                'title': 'Backend Integration',
                'description': 'Integrate mobile apps with backend services',
                'start': today + timedelta(days=40),
                'end': today + timedelta(days=70),
                'status': 'pending',
                'priority': 'high',
                'progress': 0,
                'assigned_to': 'robert_chen'
            },
            {
                'title': 'App Store Submission',
                'description': 'Submit apps to Apple App Store and Google Play',
                'start': today + timedelta(days=100),
                'end': today + timedelta(days=120),
                'status': 'pending',
                'priority': 'medium',
                'progress': 0,
                'assigned_to': 'emily_davis'
            }
        ]
        
        # Tasks for Project 3: Marketing Campaign
        project_3_tasks = [
            {
                'title': 'Market Research',
                'description': 'Conduct comprehensive market research',
                'start': today - timedelta(days=10),
                'end': today + timedelta(days=5),
                'status': 'in_progress',
                'priority': 'high',
                'progress': 70,
                'assigned_to': 'sarah_brown'
            },
            {
                'title': 'Campaign Strategy',
                'description': 'Develop overall campaign strategy and messaging',
                'start': today + timedelta(days=5),
                'end': today + timedelta(days=20),
                'status': 'pending',
                'priority': 'high',
                'progress': 0,
                'assigned_to': 'john_doe'
            },
            {
                'title': 'Content Creation',
                'description': 'Create all marketing materials and content',
                'start': today + timedelta(days=20),
                'end': today + timedelta(days=50),
                'status': 'pending',
                'priority': 'medium',
                'progress': 0,
                'assigned_to': 'sarah_brown'
            },
            {
                'title': 'Campaign Launch',
                'description': 'Execute campaign across all channels',
                'start': today + timedelta(days=50),
                'end': today + timedelta(days=80),
                'status': 'pending',
                'priority': 'critical',
                'progress': 0,
                'assigned_to': 'john_doe'
            }
        ]
        
        task_ids = {}
        
        # Insert tasks for each project
        for i, tasks in enumerate([project_1_tasks, project_2_tasks, project_3_tasks]):
            project_id = project_ids[i]['id']
            project_name = project_ids[i]['name']
            task_ids[project_id] = []
            
            for task in tasks:
                try:
                    assigned_to_id = user_ids.get(task['assigned_to'])
                    created_by_id = user_ids.get(project_ids[i]['owner'])
                    
                    self.cursor.execute("""
                        INSERT INTO tasks (
                            project_id, title, description, start_date, end_date,
                            status, priority, progress, assigned_to, created_by, color
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        project_id, task['title'], task['description'],
                        task['start'], task['end'], task['status'],
                        task['priority'], task['progress'], assigned_to_id,
                        created_by_id, project_ids[i]['owner']
                    ))
                    
                    task_id = self.cursor.lastrowid
                    task_ids[project_id].append(task_id)
                    print(f"✓ Created task: {task['title']} (Project: {project_name})")
                    
                except Exception as e:
                    print(f"✗ Failed to create task: {e}")
        
        self.connection.commit()
        return task_ids
    
    def seed_milestones(self, project_ids):
        """Create sample milestones"""
        print("\n" + "="*60)
        print("Creating milestones...")
        print("="*60)
        
        today = datetime.now().date()
        
        milestones_data = [
            # Project 1 milestones
            (project_ids[0]['id'], 'Design Approval', 'Design phase completed and approved', today + timedelta(days=21), 'upcoming'),
            (project_ids[0]['id'], 'Development Complete', 'All development work finished', today + timedelta(days=50), 'upcoming'),
            (project_ids[0]['id'], 'Go Live', 'Website launched to production', today + timedelta(days=90), 'upcoming'),
            
            # Project 2 milestones
            (project_ids[1]['id'], 'Beta Release', 'Beta version available for testing', today + timedelta(days=60), 'upcoming'),
            (project_ids[1]['id'], 'App Store Launch', 'Apps available in stores', today + timedelta(days=120), 'upcoming'),
            
            # Project 3 milestones
            (project_ids[2]['id'], 'Campaign Launch', 'Marketing campaign goes live', today + timedelta(days=50), 'upcoming'),
        ]
        
        for project_id, name, description, date, status in milestones_data:
            try:
                self.cursor.execute("""
                    INSERT INTO milestones (project_id, name, description, date, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (project_id, name, description, date, status))
                print(f"✓ Created milestone: {name}")
            except Exception as e:
                print(f"✗ Failed to create milestone: {e}")
        
        self.connection.commit()
    
    def seed_task_dependencies(self, task_ids):
        """Create task dependencies"""
        print("\n" + "="*60)
        print("Creating task dependencies...")
        print("="*60)
        
        # Get first project tasks
        if len(task_ids) > 0:
            first_project_tasks = list(task_ids.values())[0]
            
            if len(first_project_tasks) >= 7:
                # Create dependency chain for Project 1
                dependencies = [
                    (first_project_tasks[1], first_project_tasks[0]),  # Design depends on Requirements
                    (first_project_tasks[2], first_project_tasks[1]),  # Frontend depends on Design
                    (first_project_tasks[3], first_project_tasks[1]),  # Backend depends on Design
                    (first_project_tasks[4], first_project_tasks[2]),  # Content depends on Frontend
                    (first_project_tasks[4], first_project_tasks[3]),  # Content depends on Backend
                    (first_project_tasks[5], first_project_tasks[4]),  # Testing depends on Content
                    (first_project_tasks[6], first_project_tasks[5]),  # Deployment depends on Testing
                ]
                
                for task_id, depends_on in dependencies:
                    try:
                        self.cursor.execute("""
                            INSERT INTO task_dependencies (task_id, depends_on_task_id, dependency_type)
                            VALUES (%s, %s, 'finish_to_start')
                        """, (task_id, depends_on))
                        print(f"✓ Created dependency: Task {task_id} depends on Task {depends_on}")
                    except Exception as e:
                        print(f"✗ Failed to create dependency: {e}")
        
        self.connection.commit()
    
    def seed_notifications(self, user_ids, project_ids, task_ids):
        """Create sample notifications"""
        print("\n" + "="*60)
        print("Creating notifications...")
        print("="*60)
        
        notifications = [
            (user_ids['mike_wilson'], 'task_assigned', 'New Task Assigned', 'You have been assigned to "Requirements Gathering"', 'task', None),
            (user_ids['sarah_brown'], 'task_assigned', 'New Task Assigned', 'You have been assigned to "UI/UX Design"', 'task', None),
            (user_ids['john_doe'], 'deadline_alert', 'Upcoming Deadline', 'Project "Website Redesign" is due in 90 days', 'project', project_ids[0]['id']),
            (user_ids['emily_davis'], 'project_update', 'Project Updated', 'Mobile App Development has been updated', 'project', project_ids[1]['id']),
        ]
        
        for user_id, type, title, message, entity_type, entity_id in notifications:
            try:
                self.cursor.execute("""
                    INSERT INTO notifications (user_id, type, title, message, related_entity_type, related_entity_id, is_read)
                    VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                """, (user_id, type, title, message, entity_type, entity_id))
                print(f"✓ Created notification: {title}")
            except Exception as e:
                print(f"✗ Failed to create notification: {e}")
        
        self.connection.commit()
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("\n✓ Database connection closed")
    
    def seed_all(self, clear_first=False):
        """Seed all data"""
        print("="*60)
        print("DATA SEEDING SCRIPT")
        print("="*60)
        
        if not self.connect():
            return False
        
        if clear_first:
            if not self.clear_existing_data():
                print("Warning: Failed to clear data, continuing anyway...")
        
        # Seed in order
        user_ids = self.seed_users()
        project_ids = self.seed_projects(user_ids)
        self.seed_project_members(user_ids, project_ids)
        task_ids = self.seed_tasks(user_ids, project_ids)
        self.seed_milestones(project_ids)
        self.seed_task_dependencies(task_ids)
        self.seed_notifications(user_ids, project_ids, task_ids)
        
        self.close()
        
        print("\n" + "="*60)
        print("DATA SEEDING COMPLETED!")
        print("="*60)
        print(f"\n✓ Created {len(user_ids)} users")
        print(f"✓ Created {len(project_ids)} projects")
        print(f"✓ Created multiple tasks, milestones, and dependencies")
        print("\nSample Login Credentials:")
        print("  Admin: admin / admin123")
        print("  Manager: john_doe / password123")
        print("  Manager: jane_smith / password123")
        print("  Member: mike_wilson / password123")
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed database with sample data')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing data before seeding')
    
    args = parser.parse_args()
    
    if args.clear:
        print("\n⚠️  WARNING: This will clear ALL existing data!")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("✗ Seeding cancelled")
            sys.exit(0)
    
    seeder = DataSeeder()
    
    try:
        success = seeder.seed_all(clear_first=args.clear)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Seeding cancelled by user")
        seeder.close()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        seeder.close()
        sys.exit(1)


if __name__ == "__main__":
    main()

