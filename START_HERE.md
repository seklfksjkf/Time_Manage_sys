# 🚀 开始使用 - 数据库设置（密码：123456）

## 快速开始（3个步骤）

### 第1步：安装Python依赖

打开命令行，进入项目目录，运行：

```bash
pip install -r requirements.txt
```

### 第2步：创建配置文件

#### 方式A：使用快速设置脚本（推荐）

```bash
python quick_setup.py
```

#### 方式B：手动创建

在项目根目录创建一个名为 `.env` 的文件，内容如下：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=time_manage_sys

FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production-2025
JWT_SECRET_KEY=jwt-secret-key-change-in-production-2025

FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 第3步：初始化数据库并创建数据

#### 选项A：基础数据（推荐先运行这个）

```bash
python database/init_db.py
```

这会创建：
- ✅ 数据库 `time_manage_sys`
- ✅ 11张数据表
- ✅ 1个管理员账户
- ✅ 1个示例项目
- ✅ 1个示例任务

#### 选项B：完整示例数据（更多数据用于测试）

```bash
python database/seed_data.py
```

这会添加：
- ✅ 8个用户账户（不同角色）
- ✅ 5个项目
- ✅ 20+个任务
- ✅ 多个里程碑
- ✅ 任务依赖关系
- ✅ 通知数据

#### 选项C：清空并重新创建完整数据

```bash
python database/seed_data.py --clear
```

⚠️ 注意：这会清空所有现有数据！

---

## 🔑 登录凭证

### 基础数据（init_db.py）

| 用户名 | 密码 | 角色 | 邮箱 |
|--------|------|------|------|
| admin | admin123 | 管理员 | admin@timemanage.com |

### 完整数据（seed_data.py）

| 用户名 | 密码 | 角色 | 姓名 |
|--------|------|------|------|
| admin | admin123 | 管理员 | System Administrator |
| john_doe | password123 | 经理 | John Doe |
| jane_smith | password123 | 经理 | Jane Smith |
| mike_wilson | password123 | 团队成员 | Mike Wilson |
| sarah_brown | password123 | 团队成员 | Sarah Brown |
| david_lee | password123 | 团队成员 | David Lee |
| emily_davis | password123 | 团队成员 | Emily Davis |
| robert_chen | password123 | 团队成员 | Robert Chen |

---

## 📊 数据库表结构

初始化后会创建以下11张表：

| # | 表名 | 说明 |
|---|------|------|
| 1 | users | 用户账户 |
| 2 | projects | 项目信息 |
| 3 | tasks | 任务详情 |
| 4 | task_dependencies | 任务依赖关系 |
| 5 | milestones | 项目里程碑 |
| 6 | project_members | 项目成员 |
| 7 | version_history | 变更历史 |
| 8 | task_comments | 任务评论 |
| 9 | notifications | 系统通知 |
| 10 | ai_predictions | AI预测数据 |
| 11 | export_history | 导出记录 |

---

## 🔧 其他有用命令

### 重置数据库（删除所有数据）

```bash
python database/reset_db.py
```

然后重新运行初始化：

```bash
python database/init_db.py
```

### 查看帮助

```bash
python database/init_db.py --help
python database/seed_data.py --help
```

---

## ⚠️ 常见问题

### 问题1: 无法连接到MySQL

**解决方案：**
1. 确保MySQL服务正在运行
2. 检查密码是否正确（123456）
3. 确认MySQL端口是3306

### 问题2: 提示模块未找到

**解决方案：**
```bash
pip install -r requirements.txt
```

### 问题3: 编码错误

**解决方案：**
确保MySQL版本 >= 5.7，支持utf8mb4字符集

---

## ✅ 验证安装

运行初始化脚本后，你应该看到类似输出：

```
============================================================
TIME MANAGEMENT SYSTEM - DATABASE INITIALIZATION
============================================================
✓ Successfully connected to MySQL server
✓ Database 'time_manage_sys' created or already exists
✓ Successfully connected to database 'time_manage_sys'

============================================================
Creating tables...
============================================================
✓ Table 'users' created successfully
✓ Table 'projects' created successfully
...

============================================================
DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!
============================================================
```

---

## 🎯 下一步

数据库设置完成后：

1. ✅ 开发Flask后端API
2. ✅ 创建Vue.js前端界面  
3. ✅ 实现30个功能需求

---

## 📞 需要帮助？

如遇到问题，请检查：
- MySQL是否正在运行
- .env文件是否正确创建
- Python依赖是否已安装

祝您开发顺利！🚀

