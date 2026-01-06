"""
Test script to verify circular import fix
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("Testing Circular Import Fix")
print("=" * 60)

try:
    print("\n1. Testing extensions import...")
    from extensions import db, jwt
    print("   ✅ Extensions imported successfully")
    
    print("\n2. Testing app creation...")
    from app import app
    print("   ✅ App created successfully")
    
    print("\n3. Testing database models...")
    from models.user import User
    from models.project import Project
    from models.task import Task
    print("   ✅ Models imported successfully")
    
    print("\n4. Testing routes...")
    from routes.auth_routes import bp as auth_bp
    from routes.project_routes import bp as project_bp
    from routes.task_routes import bp as task_bp
    print("   ✅ Routes imported successfully")
    
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! All imports working correctly!")
    print("=" * 60)
    print("\n✅ Circular import issue is FIXED!")
    print("\n📝 Next steps:")
    print("   1. Run: cd backend")
    print("   2. Run: python app.py")
    print("   3. Server will start on http://localhost:5000")
    print("\n")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ ERROR DETECTED")
    print("=" * 60)
    print(f"\nError: {e}")
    print(f"\nError Type: {type(e).__name__}")
    import traceback
    print("\nFull Traceback:")
    traceback.print_exc()
    print("\n")

