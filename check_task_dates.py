"""
Check if tasks in database have dates
"""
import pymysql
from datetime import datetime, timedelta
from database.config import DatabaseConfig

def get_db_connection():
    """Get database connection"""
    config = DatabaseConfig()
    return pymysql.connect(**config.get_database_uri())

def check_tasks():
    """Check tasks for dates"""
    print("\n" + "="*70)
    print("    🔍 Checking Task Dates in Database")
    print("="*70)
    
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Get all tasks
        cursor.execute("""
            SELECT 
                t.id,
                t.title,
                t.start_date,
                t.end_date,
                t.status,
                p.name as project_name,
                p.id as project_id
            FROM tasks t
            JOIN projects p ON t.project_id = p.id
            ORDER BY p.id, t.id
        """)
        
        tasks = cursor.fetchall()
        
        if not tasks:
            print("\n❌ No tasks found in database!")
            print("Please run: python database/seed_data.py")
            return False
        
        print(f"\n✅ Found {len(tasks)} tasks")
        print("\n" + "-"*70)
        
        tasks_without_dates = []
        tasks_with_dates = []
        
        for task in tasks:
            project_info = f"[Project {task['project_id']}: {task['project_name']}]"
            task_info = f"Task {task['id']}: {task['title']}"
            
            if task['start_date'] and task['end_date']:
                tasks_with_dates.append(task)
                print(f"✅ {project_info} {task_info}")
                print(f"   Start: {task['start_date']}, End: {task['end_date']}")
            else:
                tasks_without_dates.append(task)
                print(f"❌ {project_info} {task_info}")
                print(f"   Start: {task['start_date']}, End: {task['end_date']}")
        
        print("\n" + "="*70)
        print(f"📊 Summary:")
        print(f"   Tasks with dates: {len(tasks_with_dates)}")
        print(f"   Tasks WITHOUT dates: {len(tasks_without_dates)}")
        print("="*70)
        
        if tasks_without_dates:
            print("\n⚠️  Some tasks don't have dates!")
            print("These tasks won't appear in the Gantt chart.")
            print("\n💡 Solution: Add dates to these tasks")
            return False
        else:
            print("\n✅ All tasks have dates!")
            print("Gantt chart should work properly.")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def add_dates_to_tasks():
    """Add dates to tasks that don't have them"""
    print("\n" + "="*70)
    print("    🔧 Adding Dates to Tasks")
    print("="*70)
    
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Get tasks without dates
        cursor.execute("""
            SELECT 
                t.id,
                t.title,
                t.project_id,
                p.start_date as project_start,
                p.end_date as project_end
            FROM tasks t
            JOIN projects p ON t.project_id = p.id
            WHERE t.start_date IS NULL OR t.end_date IS NULL
        """)
        
        tasks = cursor.fetchall()
        
        if not tasks:
            print("\n✅ All tasks already have dates!")
            return True
        
        print(f"\n📝 Found {len(tasks)} tasks without dates")
        print("Adding dates based on project timeline...\n")
        
        today = datetime.now().date()
        
        for i, task in enumerate(tasks):
            # Calculate dates based on project timeline
            project_start = task['project_start'] or today
            project_end = task['project_end'] or (today + timedelta(days=90))
            
            # Distribute tasks across project timeline
            project_duration = (project_end - project_start).days
            task_duration = max(7, project_duration // len(tasks))  # At least 7 days per task
            
            start_offset = i * task_duration
            start_date = project_start + timedelta(days=start_offset)
            end_date = start_date + timedelta(days=task_duration)
            
            # Make sure end_date doesn't exceed project end
            if end_date > project_end:
                end_date = project_end
            
            # Update task
            cursor.execute("""
                UPDATE tasks
                SET start_date = %s, end_date = %s
                WHERE id = %s
            """, (start_date, end_date, task['id']))
            
            print(f"✅ Task {task['id']}: {task['title']}")
            print(f"   Set dates: {start_date} to {end_date}")
        
        connection.commit()
        print(f"\n✅ Updated {len(tasks)} tasks with dates!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("    🔍 Task Date Checker and Fixer")
    print("="*70)
    
    # First, check current status
    has_dates = check_tasks()
    
    if not has_dates:
        print("\n" + "="*70)
        response = input("\n❓ Do you want to add dates to tasks without dates? (y/n): ")
        if response.lower() == 'y':
            if add_dates_to_tasks():
                print("\n" + "="*70)
                print("✅ Done! Checking again...")
                check_tasks()
        else:
            print("\n💡 You can manually add dates through the web interface:")
            print("   1. Go to Project Details")
            print("   2. Click on a task to edit")
            print("   3. Set Start Date and End Date")
            print("   4. Save")
    
    print("\n" + "="*70)
    print("✅ Check complete!")
    print("="*70)

