# Time Management System

> A comprehensive project and task management system with interactive Gantt chart visualization

![Version](https://img.shields.io/badge/Version-1.2-blue.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.0-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Implementation](https://img.shields.io/badge/Implementation-85%25-brightgreen.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Feature Comparison](#feature-comparison)
- [Tech Stack](#tech-stack)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

Time Management System is a full-stack web application designed for efficient project and task management. It features an **interactive Gantt chart** with drag-and-drop capabilities, milestone tracking, and a modern, visually appealing interface.

**Current Status**: Version 1.0 - Core features fully implemented, advanced reporting and AI features planned for future releases.

### Key Highlights (Implemented ✅)

- **Interactive Gantt Chart**: Drag, resize, and edit tasks directly on the timeline
- **Multiple Views**: Switch between Daily, Weekly, and Monthly views
- **Milestone Tracking**: Visual milestone indicators with dates in task list
- **Split Layout**: Task list on top, full Gantt chart on bottom
- **Responsive Design**: Modern, gradient-based UI with smooth animations
- **Role-based Access**: Admin, Manager, and Member roles with different permissions

### Recently Added Features ✨

- **Advanced Reporting**: Progress reports with detailed statistics and charts
- **Critical Path Analysis**: Identifies tasks affecting project completion
- **Export Functionality**: Export to JSON, CSV, and PDF (via print)
- **Version History**: Track changes to projects and tasks
- **Enhanced Dashboard**: Project status distribution and quick actions

## ✨ Features

### ✅ Implemented Features

#### Project Management
- ✅ Create, update, and delete projects
- ✅ Assign team members with specific roles
- ✅ Track project progress with completion percentages
- ✅ Set project deadlines and priorities

#### Task Management
- ✅ Create and manage tasks with detailed information
- ✅ Assign tasks to team members
- ✅ Set task priorities (Low, Medium, High, Critical)
- ✅ Track task status (Pending, In Progress, Completed, Blocked, Cancelled)
- ✅ Task dependencies (database support, UI in progress)
- ✅ Comment on tasks (database support, UI in progress)

#### Interactive Gantt Chart
- ✅ **Drag & Drop**: Move tasks by dragging task bars to change dates
- ✅ **Resize**: Adjust task duration by dragging edges
- ✅ **Edit**: Click edit button to modify task details
- ✅ **Delete**: Remove tasks with confirmation dialog
- ✅ **Add**: Create new tasks via dialog
- ✅ **Zoom Levels**: Daily (40px/day), Weekly (20px/day), Monthly (8px/day)
- ✅ **Auto-scroll**: Synchronized header and timeline scrolling
- ✅ **Split View**: Task list on top, full Gantt chart on bottom
- ✅ **Month Alignment**: Perfect alignment between month labels and date columns

#### Milestones
- ✅ Create project milestones
- ✅ Track milestone dates
- ✅ Color-coded milestone display in task list
- ✅ Milestone status tracking (Upcoming, Completed, Missed)

#### Dashboard
- ✅ Basic project overview statistics
- ✅ Task completion metrics
- ✅ Recent activity feed
- ✅ Upcoming deadlines
- ✅ **Project Status Distribution**: Visual breakdown by status
- ✅ **Quick Actions**: Fast access to common operations
- ✅ **Report Generation**: Quick access to project reports

#### Reporting & Export
- ✅ **Progress Reports**: Comprehensive project progress analysis
  - Task statistics (total, completed, in progress, pending, blocked)
  - Completion rate and average progress
  - Milestone tracking
  - Timeline analysis (elapsed/remaining days)
  - Overdue and upcoming tasks
  - Team member performance stats
- ✅ **Critical Path Analysis**: Identifies task dependencies affecting project completion
- ✅ **Export Options**:
  - JSON export with full project data
  - CSV export for Excel compatibility
  - PDF export via browser print dialog
- ✅ **Export History**: Tracks all export operations

#### Version Control
- ✅ **Version History Tracking**:
  - Automatic tracking of project changes
  - Task modification history
  - Change timestamps and user attribution
  - Timeline view of all modifications
  - Displays in project detail sidebar

#### Notifications
- ✅ Notification system (database support)
- ✅ Task assignment notifications
- ✅ Deadline reminders
- ✅ Project update alerts

### 🔶 Partially Implemented (Database Ready, UI Pending)
- 🔶 Task dependencies visualization in Gantt chart
- 🔶 Task comments display and management
- 🔶 AI predictions integration (duration estimation, risk alerts)

### ❌ Not Yet Implemented

#### Smart/AI Features
- ❌ Task Duration Estimation
- ❌ Deadline Risk Alerts
- ❌ Resource Allocation Suggestions
- ❌ Automated Scheduling
- ❌ Project Success Prediction

## 📊 Feature Comparison

Below is a detailed comparison of features from the original requirements vs current implementation:

| # | Feature | Category | Status | Notes |
|---|---------|----------|--------|-------|
| 1 | User Authentication | Core | ✅ Implemented | Login/Register/JWT |
| 2 | Project CRUD | Core | ✅ Implemented | Full CRUD operations |
| 3 | Task CRUD | Core | ✅ Implemented | Full CRUD operations |
| 4 | Interactive Gantt Chart | Core | ✅ Implemented | Drag, resize, edit |
| 5 | Multiple Zoom Levels | Core | ✅ Implemented | Daily/Weekly/Monthly |
| 6 | Milestone Tracking | Core | ✅ Implemented | Display in task list |
| 7 | Task Assignment | Core | ✅ Implemented | Assign to team members |
| 8 | Status & Priority | Core | ✅ Implemented | 5 statuses, 4 priorities |
| 9 | Dashboard | Core | ✅ Implemented | Basic statistics |
| 10 | Notifications | Core | ✅ Implemented | Database support |
| 11 | Task Dependencies | Core | 🔶 Partial | Database ready, UI pending |
| 12 | Task Comments | Core | 🔶 Partial | Database ready, UI pending |
| 13 | Team Management | Core | ✅ Implemented | Project members |
| 14 | Role-based Access | Core | ✅ Implemented | Admin/Manager/Member |
| 21 | Project Progress Report | Reporting | ✅ Implemented | Full statistics & charts |
| 22 | Critical Path Highlighting | Reporting | ✅ Implemented | DFS algorithm + UI display |
| 23 | Export Timeline | Reporting | ✅ Implemented | JSON/CSV/PDF export |
| 24 | Version History | Reporting | ✅ Implemented | Full tracking + timeline UI |
| 25 | Project Dashboard | Reporting | ✅ Implemented | Enhanced with quick actions |
| 26 | Task Duration Estimation | AI/Smart | ❌ Not Implemented | Planned v2.0 |
| 27 | Deadline Risk Alerts | AI/Smart | ❌ Not Implemented | Planned v2.0 |
| 28 | Resource Allocation | AI/Smart | ❌ Not Implemented | Planned v2.0 |
| 29 | Automated Scheduling | AI/Smart | ❌ Not Implemented | Planned v2.0 |
| 30 | Success Prediction | AI/Smart | ❌ Not Implemented | Planned v2.0 |

### Summary
- **✅ Fully Implemented**: 19 features (63%)
- **🔶 Partially Implemented**: 2 features (7%)
- **❌ Not Implemented**: 9 features (30%)

### Current Version: 1.2
**Focus**: Core project and task management with interactive Gantt chart, advanced reporting, and export capabilities

### Future Version: 2.0 (AI/Smart Features)
**Focus**: AI-powered predictions, risk alerts, automated scheduling, resource allocation

### Recent Updates (v1.2)
- ✅ Project Progress Reports with comprehensive statistics
- ✅ Critical Path Analysis using DFS algorithm
- ✅ Export functionality (JSON, CSV, PDF)
- ✅ Version History tracking and timeline UI
- ✅ Enhanced Dashboard with status distribution and quick actions

## 🛠 Tech Stack

### Backend
- **Framework**: Flask 2.3.0
- **Database**: MySQL 8.0+
- **ORM**: Flask-SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Password Hashing**: Werkzeug Security
- **CORS**: Flask-CORS
- **Database Driver**: PyMySQL

### Frontend
- **Framework**: Vue.js 3.x
- **Build Tool**: Vite
- **State Management**: Pinia
- **UI Components**: Element Plus
- **HTTP Client**: Axios
- **Routing**: Vue Router
- **Icons**: Element Plus Icons

### Database
- **RDBMS**: MySQL 8.0+
- **Tables**: 11 relational tables
- **Features**: Foreign keys, cascading deletes, auto-timestamps

## 💻 System Requirements

### Required Software
- **Python**: 3.8 or higher
- **Node.js**: 14.x or higher
- **npm**: 6.x or higher
- **MySQL**: 8.0 or higher

### Recommended System
- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Time_Manage_sys
```

### 2. Database Setup

**Option A: Quick Setup (Recommended)**
```bash
python quick_setup.py
```
This will create `database/config.py` with default settings (password: 123456).

**Option B: Interactive Setup**
```bash
python setup_wizard.py
```
Follow the prompts to configure your database connection.

### 3. Initialize Database

```bash
python database/init_db.py
```

### 4. Seed Sample Data (Optional)

```bash
python database/seed_data.py
```

This creates:
- 4 users (admin, john_doe, jane_smith, mike_wilson)
- 3 projects
- Multiple tasks and milestones
- Sample notifications

### 5. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 6. Start Backend Server

```bash
cd backend
python app.py
```

Backend will run on `http://localhost:5000`

### 7. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 8. Start Frontend Development Server

```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

### 9. Login

Default credentials:
- **Admin**: `admin` / `admin123`
- **Manager**: `john_doe` / `password123`
- **Member**: `mike_wilson` / `password123`

## 📖 How to Use New Features

### 1. Project Progress Reports

**Accessing Reports:**
1. Navigate to a project detail page
2. Click the "View Report" button in the header
3. View comprehensive statistics including:
   - Task completion rates and averages
   - Milestone progress
   - Timeline analysis (days elapsed/remaining)
   - Overdue and upcoming tasks
   - Team member performance
   - **Critical Path**: Tasks that directly impact project completion

**Exporting Reports:**
- Click the "Export" dropdown button
- Choose format: JSON, CSV/Excel, or PDF
- JSON: Full project data in JSON format
- CSV: Task list in spreadsheet-compatible format
- PDF: Use browser print dialog to save as PDF

### 2. Critical Path Analysis

The system automatically identifies the critical path - the longest sequence of dependent tasks that determines the project completion date.

**Viewing Critical Path:**
- Open a project's progress report
- Scroll to the "Critical Path" section
- Tasks are numbered in sequence
- Shows task priority, status, and date range
- Focus on these tasks to prevent project delays

### 3. Enhanced Dashboard

**New Dashboard Features:**
- **Project Status Distribution**: Visual breakdown by status (Planning, In Progress, On Hold, Completed)
- **Quick Actions**: Fast access to create projects, view tasks, check notifications, and generate reports
- **Report Generation**: Click "Generate Report" to select a project and view its detailed progress report

### 4. Version History

**Viewing Version History:**
1. Navigate to a project detail page
2. Look at the right sidebar
3. Find the "Version History" card below team members
4. View recent changes with timestamps
5. Click the refresh button to reload history

**What's Tracked:**
- Project updates (name, dates, status changes)
- Task modifications (all field changes)
- Who made the change and when
- Change type (created, updated, deleted)

### 5. Interactive Gantt Chart

**Basic Operations:**
- **Zoom**: Use Daily/Weekly/Monthly buttons to change view
- **Drag**: Click and drag task bars to change dates
- **Resize**: Drag left/right edges to adjust duration
- **Edit**: Click edit button in task list to modify details
- **Delete**: Click delete button with confirmation
- **Add**: Use "Add Task" button in header

**Milestones:**
- Displayed in the rightmost column of task list
- Color-coded cards with milestone name and date
- Visible alongside task information

## 📁 Project Structure

```
Time_Manage_sys/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── extensions.py          # Flask extensions (db, jwt)
│   ├── utils.py              # Utility functions
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   ├── milestone.py
│   │   └── ...
│   └── routes/               # API routes
│       ├── auth_routes.py
│       ├── project_routes.py
│       ├── task_routes.py
│       ├── timeline_routes.py
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── components/       # Vue components
│   │   │   └── GanttChart.vue
│   │   ├── views/           # Page views
│   │   │   ├── Dashboard.vue
│   │   │   ├── projects/
│   │   │   └── tasks/
│   │   ├── router/          # Vue Router
│   │   ├── stores/          # Pinia stores
│   │   └── services/        # API services
│   └── vite.config.js
├── database/
│   ├── config.py            # Database configuration
│   ├── init_db.py           # Database initialization
│   ├── reset_db.py          # Reset database
│   └── seed_data.py         # Sample data seeder
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 📚 API Documentation

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### Projects

#### Get All Projects
```http
GET /api/projects
Authorization: Bearer <token>
```

#### Create Project
```http
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "start_date": "2025-01-01T00:00:00.000Z",
  "deadline": "2025-12-31T00:00:00.000Z",
  "status": "active",
  "priority": "high"
}
```

#### Get Project Timeline
```http
GET /api/timeline/projects/:id
Authorization: Bearer <token>
```

### Tasks

#### Create Task
```http
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 1,
  "title": "string",
  "description": "string",
  "start_date": "2025-01-01T00:00:00.000Z",
  "end_date": "2025-01-15T00:00:00.000Z",
  "status": "pending",
  "priority": "high",
  "assigned_to": 2
}
```

#### Update Task
```http
PUT /api/tasks/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "string",
  "status": "in_progress",
  "progress": 50
}
```

## 🗄 Database Schema

### Core Tables

#### users
- `id` (PK)
- `username` (unique)
- `email` (unique)
- `password_hash`
- `full_name`
- `role` (admin/manager/member)
- `created_at`, `updated_at`

#### projects
- `id` (PK)
- `name`
- `description`
- `start_date`, `deadline`
- `status` (planning/active/on_hold/completed/cancelled)
- `priority` (low/medium/high/critical)
- `created_by` (FK -> users)
- `created_at`, `updated_at`

#### tasks
- `id` (PK)
- `project_id` (FK -> projects)
- `title`, `description`
- `start_date`, `end_date`
- `status` (pending/in_progress/completed/blocked/cancelled)
- `priority` (low/medium/high/critical)
- `progress` (0-100)
- `assigned_to` (FK -> users)
- `created_at`, `updated_at`

#### milestones
- `id` (PK)
- `project_id` (FK -> projects)
- `name`, `description`
- `date`
- `status` (upcoming/completed/missed)
- `color` (hex color code)
- `created_at`, `updated_at`

### Additional Tables
- **project_members**: Team assignments
- **task_dependencies**: Task relationships
- **task_comments**: Task discussions
- **notifications**: User notifications
- **version_history**: Change tracking
- **ai_predictions**: AI-powered insights
- **export_history**: Export logs

## 🎨 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Gantt Chart
![Gantt Chart](screenshots/gantt-chart.png)

### Project List
![Projects](screenshots/projects.png)

## 🔧 Configuration

### Database Configuration

Edit `database/config.py`:

```python
class DatabaseConfig:
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = 'your_password'
    DB_NAME = 'time_management'
```

### Backend Configuration

Edit `backend/app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://...'
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
```

### Frontend Configuration

Edit `frontend/vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

## 🧪 Testing

### Test Backend
```bash
cd backend
python -m pytest tests/
```

### Test Frontend
```bash
cd frontend
npm run test
```

### Manual Testing
1. Open `test_frontend_api.html` in browser
2. Test API endpoints manually
3. Check browser console for errors

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check MySQL is running
mysql -u root -p

# Reset database
python database/reset_db.py
python database/init_db.py
```

### JWT Token Issues
```bash
# Clear browser localStorage
# Restart backend server
python backend/app.py
```

### Frontend Build Issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8
- **JavaScript**: Use ESLint with Vue.js recommended config
- **Vue**: Use Composition API with `<script setup>`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Developer**: Your Name
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- **Flask** - Micro web framework
- **Vue.js** - Progressive JavaScript framework
- **Element Plus** - Vue 3 component library
- **MySQL** - Relational database
- **Community** - All contributors and users

## 📞 Support

For support, email your.email@example.com or open an issue on GitHub.

## ✅ Implemented Features (Current Version)

### Core Features ✅
- [x] User authentication and authorization
- [x] Project management (CRUD)
- [x] Task management (CRUD)
- [x] Interactive Gantt chart with drag & drop
- [x] Task resize to adjust duration
- [x] Three zoom levels (Daily/Weekly/Monthly)
- [x] Milestone tracking and display
- [x] Task status and priority management
- [x] Team member assignment
- [x] Basic dashboard
- [x] Notification system
- [x] Task dependencies (database support)
- [x] Comments on tasks (database support)

### Database Support (Ready but UI not implemented) 🔶
- [x] Version history tracking (database table)
- [x] AI predictions (database table)
- [x] Export history (database table)
- [x] Task dependencies (database table)

## 🗺 Roadmap

### Version 1.5 (Next Release) - Reporting & Export
- [ ] **Project Progress Report** - Generate summaries of completed vs pending tasks
- [ ] **Critical Path Highlighting** - Identify tasks that affect project completion date
- [ ] **Export Timeline** - Export as PDF, PNG, or Excel for sharing
- [ ] **Version History UI** - Keep track of changes to tasks and dates
- [ ] **Enhanced Project Dashboard** - Overview of all projects with status indicators

### Version 2.0 (Planned) - Smart/AI Features
- [ ] **Task Duration Estimation** - Suggest expected durations based on past tasks
- [ ] **Deadline Risk Alerts** - Predict potential deadline overruns
- [ ] **Resource Allocation Suggestions** - Recommend team members for tasks based on workload
- [ ] **Automated Scheduling** - Suggest optimal timelines when tasks overlap
- [ ] **Project Success Prediction** - AI model estimates probability of finishing on time

### Version 2.5 (Future)
- [ ] Real-time collaboration with WebSocket
- [ ] Mobile application (React Native)
- [ ] Integration with Slack/Teams/Jira
- [ ] Advanced analytics dashboard
- [ ] Budget tracking and resource planning
- [ ] Gantt chart templates
- [ ] Bulk import/export

---

## 📊 Project Statistics

- **Backend Files**: 20+ Python files
- **Frontend Files**: 30+ Vue/JS files  
- **Database Tables**: 11 relational tables
- **API Endpoints**: 50+ RESTful APIs
- **Lines of Code**: 10,000+ lines

### Implementation Status
- **✅ Core Features**: 100% Complete (14/14 features)
- **🔶 Database Support**: Ready for advanced features
- **❌ Advanced Features**: Planned for v1.5 and v2.0 (12/30 features)
- **Overall Progress**: ~60% Complete

**Version 1.0 Core System is fully functional and production-ready!** 🎉

---

**Made with ❤️ using Flask & Vue.js**

