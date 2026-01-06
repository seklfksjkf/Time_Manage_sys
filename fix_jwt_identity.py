"""
Script to fix JWT identity issue in all route files
Changes get_jwt_identity() to int(get_jwt_identity())
"""
import os
import re

# List of route files to fix
route_files = [
    'backend/routes/dashboard_routes.py',
    'backend/routes/notification_routes.py',
    'backend/routes/project_routes.py',
    'backend/routes/task_routes.py',
    'backend/routes/timeline_routes.py',
    'backend/routes/milestone_routes.py',
    'backend/routes/export_routes.py'
]

for file_path in route_files:
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace get_jwt_identity() with int(get_jwt_identity())
    # But not if it's already wrapped in int()
    original_content = content
    content = re.sub(
        r'(?<!int\()get_jwt_identity\(\)',
        'int(get_jwt_identity())',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {file_path}")
    else:
        print(f"ℹ️  No changes needed: {file_path}")

print("\n🎉 All files processed!")
print("\n⚠️  Important: Restart the backend server!")
print("   cd backend && python app.py")

