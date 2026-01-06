"""
检查即将到期任务的调试脚本
"""
import sys
sys.path.insert(0, 'backend')

from extensions import db
from models.task import Task
from models.user import User
from models.project import Project
from datetime import datetime, timedelta
from database.config import DatabaseConfig

# 创建数据库连接
import pymysql
connection = pymysql.connect(
    host=DatabaseConfig.DB_HOST,
    user=DatabaseConfig.DB_USER,
    password=DatabaseConfig.DB_PASSWORD,
    database=DatabaseConfig.DB_NAME,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

print("\n" + "="*80)
print("🔍 检查即将到期的任务（Upcoming Deadlines）")
print("="*80)

try:
    with connection.cursor() as cursor:
        # 1. 检查所有用户
        print("\n📋 用户列表：")
        cursor.execute("SELECT id, username, full_name FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"  - ID: {user['id']}, Username: {user['username']}, Name: {user['full_name']}")
        
        # 2. 检查所有任务
        print("\n📋 所有任务：")
        cursor.execute("""
            SELECT 
                t.id, 
                t.title, 
                t.assigned_to,
                t.end_date,
                t.status,
                u.username as assignee_name
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.id
            ORDER BY t.end_date
        """)
        tasks = cursor.fetchall()
        
        if not tasks:
            print("  ⚠️ 数据库中没有任何任务！")
        else:
            for task in tasks:
                print(f"\n  任务 #{task['id']}: {task['title']}")
                print(f"    - 分配给: {task['assignee_name'] or '未分配'} (ID: {task['assigned_to']})")
                print(f"    - 截止日期: {task['end_date']}")
                print(f"    - 状态: {task['status']}")
        
        # 3. 检查符合"Upcoming Deadlines"条件的任务
        print("\n" + "="*80)
        print("🎯 符合「Upcoming Deadlines」条件的任务：")
        print("="*80)
        
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        print(f"\n时间范围: {today} 到 {next_week}")
        
        for user in users:
            user_id = user['id']
            print(f"\n👤 用户: {user['username']} (ID: {user_id})")
            
            cursor.execute("""
                SELECT 
                    id, 
                    title, 
                    end_date,
                    status
                FROM tasks
                WHERE assigned_to = %s
                  AND end_date >= %s
                  AND end_date <= %s
                  AND status != 'completed'
                ORDER BY end_date
                LIMIT 5
            """, (user_id, today, next_week))
            
            upcoming = cursor.fetchall()
            
            if upcoming:
                print(f"  ✅ 找到 {len(upcoming)} 个即将到期的任务：")
                for task in upcoming:
                    days_until = (task['end_date'] - today).days
                    print(f"    - [{task['status']}] {task['title']}")
                    print(f"      截止: {task['end_date']} ({days_until}天后)")
            else:
                print("  ❌ 没有找到符合条件的任务")
                
                # 详细分析原因
                cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s", (user_id,))
                total = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s AND status = 'completed'", (user_id,))
                completed = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s AND end_date < %s", (user_id, today))
                past = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE assigned_to = %s AND end_date > %s", (user_id, next_week))
                future = cursor.fetchone()['count']
                
                print(f"  原因分析：")
                print(f"    - 总任务数: {total}")
                print(f"    - 已完成: {completed}")
                print(f"    - 已过期: {past}")
                print(f"    - 7天后到期: {future}")
        
        # 4. 推荐操作
        print("\n" + "="*80)
        print("💡 建议：")
        print("="*80)
        
        if not tasks:
            print("1. 数据库中没有任务，请先创建任务")
            print("2. 确保任务分配给了用户（assigned_to 字段）")
        else:
            unassigned = [t for t in tasks if not t['assigned_to']]
            if unassigned:
                print(f"⚠️ 发现 {len(unassigned)} 个未分配的任务，请分配给用户")
            
            all_completed = all(t['status'] == 'completed' for t in tasks)
            if all_completed:
                print("⚠️ 所有任务都已完成，请创建新任务或修改任务状态")
            
            out_of_range = [t for t in tasks if t['end_date'] and (t['end_date'] < today or t['end_date'] > next_week)]
            if out_of_range:
                print(f"⚠️ {len(out_of_range)} 个任务的截止日期不在未来7天内")
        
        print("\n3. 检查前端是否使用正确的用户登录")
        print("4. 确保后端服务已重启")
        
finally:
    connection.close()

print("\n" + "="*80 + "\n")

