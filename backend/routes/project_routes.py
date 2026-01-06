"""
Project Management API Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.project import Project
from models.project_member import ProjectMember
from models.version_history import VersionHistory
from datetime import datetime, date
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import parse_datetime

bp = Blueprint('projects', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    """List all projects for current user"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get projects owned by user or where user is a member
        owned_projects = Project.query.filter_by(owner_id=current_user_id).all()
        member_projects = Project.query.join(ProjectMember).filter(
            ProjectMember.user_id == current_user_id
        ).all()
        
        # Combine and remove duplicates
        all_projects = {p.id: p for p in owned_projects + member_projects}
        projects = list(all_projects.values())
        
        return jsonify({
            'projects': [p.to_dict(include_relations=True) for p in projects]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create new project"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation
        if 'name' not in data:
            return jsonify({'error': 'Project name is required'}), 400
        
        # Create project
        project = Project(
            name=data['name'],
            description=data.get('description'),
            owner_id=current_user_id,
            start_date=parse_datetime(data.get('start_date')),
            end_date=parse_datetime(data.get('end_date')),
            deadline=parse_datetime(data.get('deadline')),
            status=data.get('status', 'planning'),
            color=data.get('color', '#3498db')
        )
        
        db.session.add(project)
        db.session.flush()  # Get project ID
        
        # Add creator as owner member
        member = ProjectMember(
            project_id=project.id,
            user_id=current_user_id,
            role='owner'
        )
        db.session.add(member)
        
        # Log version history
        history = VersionHistory(
            entity_type='project',
            entity_id=project.id,
            action='created',
            changed_by=current_user_id,
            changes={'name': project.name}
        )
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict(include_relations=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get project details"""
    try:
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check access
        is_member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user_id
        ).first()
        
        if project.owner_id != current_user_id and not is_member:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'project': project.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update project"""
    try:
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permission (owner or manager)
        member = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=current_user_id
        ).first()
        
        if project.owner_id != current_user_id and (not member or member.role not in ['owner', 'manager']):
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        old_values = {}
        
        # Update fields
        if 'name' in data:
            old_values['name'] = project.name
            project.name = data['name']
        if 'description' in data:
            old_values['description'] = project.description
            project.description = data['description']
        if 'start_date' in data:
            project.start_date = parse_datetime(data.get('start_date'))
        if 'end_date' in data:
            project.end_date = parse_datetime(data.get('end_date'))
        if 'deadline' in data:
            project.deadline = parse_datetime(data.get('deadline'))
        if 'status' in data:
            old_values['status'] = project.status
            project.status = data['status']
        if 'color' in data:
            project.color = data['color']
        
        # Log version history
        if old_values:
            history = VersionHistory(
                entity_type='project',
                entity_id=project_id,
                action='updated',
                changed_by=current_user_id,
                changes=old_values
            )
            db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete project"""
    try:
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Only owner can delete
        if project.owner_id != current_user_id:
            return jsonify({'error': 'Only project owner can delete project'}), 403
        
        # Log version history
        history = VersionHistory(
            entity_type='project',
            entity_id=project_id,
            action='deleted',
            changed_by=current_user_id,
            changes={'name': project.name}
        )
        db.session.add(history)
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>/members', methods=['GET'])
@jwt_required()
def get_project_members(project_id):
    """Get project team members"""
    try:
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        
        return jsonify({
            'members': [m.to_dict() for m in members]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>/members', methods=['POST'])
@jwt_required()
def add_project_member(project_id):
    """Add member to project"""
    try:
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permission
        if project.owner_id != current_user_id:
            member = ProjectMember.query.filter_by(
                project_id=project_id,
                user_id=current_user_id
            ).first()
            if not member or member.role not in ['owner', 'manager']:
                return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        if 'user_id' not in data:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Check if already a member
        existing = ProjectMember.query.filter_by(
            project_id=project_id,
            user_id=data['user_id']
        ).first()
        
        if existing:
            return jsonify({'error': 'User is already a member'}), 409
        
        # Add member
        new_member = ProjectMember(
            project_id=project_id,
            user_id=data['user_id'],
            role=data.get('role', 'member')
        )
        
        db.session.add(new_member)
        db.session.commit()
        
        return jsonify({
            'message': 'Member added successfully',
            'member': new_member.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
def remove_project_member(project_id, member_id):
    """Remove member from project"""
    try:
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check permission
        if project.owner_id != current_user_id:
            return jsonify({'error': 'Only project owner can remove members'}), 403
        
        member = ProjectMember.query.get(member_id)
        
        if not member or member.project_id != project_id:
            return jsonify({'error': 'Member not found'}), 404
        
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Member removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>/progress-report', methods=['GET'])
@jwt_required()
def get_progress_report(project_id):
    """Get detailed progress report for a project"""
    try:
        from models.task import Task
        from models.milestone import Milestone
        from sqlalchemy import func
        
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get all tasks for the project
        tasks = Task.query.filter_by(project_id=project_id).all()
        
        # Calculate task statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in_progress'])
        pending_tasks = len([t for t in tasks if t.status == 'pending'])
        blocked_tasks = len([t for t in tasks if t.status == 'blocked'])
        cancelled_tasks = len([t for t in tasks if t.status == 'cancelled'])
        
        # Calculate progress percentage
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average progress
        avg_progress = sum([t.progress for t in tasks]) / total_tasks if total_tasks > 0 else 0
        
        # Tasks by priority
        high_priority = len([t for t in tasks if t.priority == 'high'])
        critical_priority = len([t for t in tasks if t.priority == 'critical'])
        
        # Overdue tasks
        today = datetime.now().date()
        overdue_tasks = []
        for task in tasks:
            if task.end_date and task.status not in ['completed', 'cancelled']:
                # Handle both date and datetime objects
                task_end = task.end_date if isinstance(task.end_date, date) else task.end_date.date()
                if task_end < today:
                    overdue_tasks.append(task.to_dict())
        
        # Upcoming deadlines (next 7 days)
        from datetime import timedelta
        next_week = today + timedelta(days=7)
        upcoming_tasks = []
        for task in tasks:
            if task.end_date and task.status not in ['completed', 'cancelled']:
                # Handle both date and datetime objects
                task_date = task.end_date if isinstance(task.end_date, date) else task.end_date.date()
                if today <= task_date <= next_week:
                    upcoming_tasks.append(task.to_dict())
        
        # Recently completed tasks (last 7 days)
        week_ago = today - timedelta(days=7)
        recent_completed = []
        for task in tasks:
            if task.status == 'completed' and task.updated_at:
                # Handle both date and datetime objects
                updated_date = task.updated_at if isinstance(task.updated_at, date) else task.updated_at.date()
                if updated_date >= week_ago:
                    recent_completed.append(task.to_dict())
        
        # Get milestones
        milestones = Milestone.query.filter_by(project_id=project_id).all()
        completed_milestones = len([m for m in milestones if m.status == 'completed'])
        total_milestones = len(milestones)
        
        # Task distribution by assignee
        assignee_stats = {}
        for task in tasks:
            if task.assigned_to:
                if task.assigned_to not in assignee_stats:
                    # Get assignee name through relationship
                    assignee_name = task.assignee.full_name if task.assignee else 'Unknown'
                    assignee_stats[task.assigned_to] = {
                        'total': 0,
                        'completed': 0,
                        'in_progress': 0,
                        'assignee_name': assignee_name
                    }
                assignee_stats[task.assigned_to]['total'] += 1
                if task.status == 'completed':
                    assignee_stats[task.assigned_to]['completed'] += 1
                elif task.status == 'in_progress':
                    assignee_stats[task.assigned_to]['in_progress'] += 1
        
        # Calculate Critical Path (simple version based on longest chain)
        from models.task_dependency import TaskDependency
        critical_path_tasks = []
        
        # Get all task dependencies
        # Note: TaskDependency uses task_id and depends_on_task_id
        task_ids = [t.id for t in tasks]
        dependencies = TaskDependency.query.filter(
            TaskDependency.task_id.in_(task_ids)
        ).all()
        
        # Build dependency graph
        # Key: task_id, Value: list of tasks that depend on this task
        task_graph = {t.id: [] for t in tasks}
        reverse_deps = {t.id: [] for t in tasks}  # Track what each task depends on
        
        for dep in dependencies:
            # dep.task_id depends on dep.depends_on_task_id
            if dep.depends_on_task_id in task_graph:
                task_graph[dep.depends_on_task_id].append(dep.task_id)
            if dep.task_id in reverse_deps:
                reverse_deps[dep.task_id].append(dep.depends_on_task_id)
        
        # Find longest path (critical path) using simple DFS
        def get_task_duration(task_id):
            task = next((t for t in tasks if t.id == task_id), None)
            if task and task.start_date and task.end_date:
                return (task.end_date - task.start_date).days + 1
            return 1
        
        def dfs_longest_path(task_id, visited, path):
            visited.add(task_id)
            path.append(task_id)
            
            max_path = list(path)
            max_duration = sum(get_task_duration(tid) for tid in path)
            
            for next_task in task_graph.get(task_id, []):
                if next_task not in visited:
                    result_path = dfs_longest_path(next_task, visited, path)
                    result_duration = sum(get_task_duration(tid) for tid in result_path)
                    if result_duration > max_duration:
                        max_path = result_path
                        max_duration = result_duration
            
            path.pop()
            visited.remove(task_id)
            return max_path
        
        # Find tasks with no dependencies (start tasks)
        # These are tasks that don't depend on any other task
        dependent_task_ids = set(dep.task_id for dep in dependencies)
        start_tasks = [t.id for t in tasks if t.id not in dependent_task_ids]
        
        # If no dependencies exist, just return empty critical path
        if not dependencies or not start_tasks:
            critical_path_tasks = []
        else:
            longest_path = []
            for start_task in start_tasks:
                path = dfs_longest_path(start_task, set(), [])
                if len(path) > len(longest_path):
                    longest_path = path
            
            critical_path_tasks = [t.to_dict() for t in tasks if t.id in longest_path]
        
        # Project timeline
        project_days = 0
        days_elapsed = 0
        days_remaining = 0
        
        if project.start_date and project.deadline:
            # Handle both date and datetime objects
            start_date = project.start_date if isinstance(project.start_date, date) else project.start_date.date()
            deadline = project.deadline if isinstance(project.deadline, date) else project.deadline.date()
            
            project_days = (deadline - start_date).days
            days_elapsed = (today - start_date).days if start_date <= today else 0
            days_remaining = (deadline - today).days if deadline >= today else 0
        
        return jsonify({
            'project': project.to_dict(),
            'summary': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': pending_tasks,
                'blocked_tasks': blocked_tasks,
                'cancelled_tasks': cancelled_tasks,
                'completion_rate': round(completion_rate, 2),
                'average_progress': round(avg_progress, 2),
                'high_priority_tasks': high_priority,
                'critical_priority_tasks': critical_priority,
                'overdue_count': len(overdue_tasks),
                'upcoming_count': len(upcoming_tasks)
            },
            'milestones': {
                'total': total_milestones,
                'completed': completed_milestones,
                'completion_rate': round((completed_milestones / total_milestones * 100) if total_milestones > 0 else 0, 2)
            },
            'timeline': {
                'project_days': project_days,
                'days_elapsed': days_elapsed,
                'days_remaining': days_remaining,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'deadline': project.deadline.isoformat() if project.deadline else None
            },
            'overdue_tasks': overdue_tasks,
            'upcoming_tasks': upcoming_tasks,
            'recent_completed': recent_completed,
            'critical_path': critical_path_tasks,
            'assignee_stats': [
                {
                    'user_id': user_id,
                    'name': stats['assignee_name'],
                    'total': stats['total'],
                    'completed': stats['completed'],
                    'in_progress': stats['in_progress'],
                    'completion_rate': round((stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0, 2)
                }
                for user_id, stats in assignee_stats.items()
            ]
        }), 200
        
    except Exception as e:
        print(f"Error generating progress report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:project_id>/version-history', methods=['GET'])
@jwt_required()
def get_version_history(project_id):
    """Get version history for a project"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get version history from version_history table
        # Note: VersionHistory uses entity_type and entity_id
        history = VersionHistory.query.filter_by(
            entity_type='project',
            entity_id=project_id
        ).order_by(VersionHistory.changed_at.desc()).limit(50).all()
        
        # Also get task version history
        from models.task import Task
        tasks = Task.query.filter_by(project_id=project_id).all()
        task_ids = [t.id for t in tasks]
        
        if task_ids:
            task_history = VersionHistory.query.filter(
                VersionHistory.entity_type == 'task',
                VersionHistory.entity_id.in_(task_ids)
            ).order_by(VersionHistory.changed_at.desc()).limit(50).all()
        else:
            task_history = []
        
        # Combine and sort all history
        all_history = history + task_history
        all_history.sort(key=lambda x: x.changed_at, reverse=True)
        
        # Enhance with more readable information
        result = []
        for h in all_history[:50]:
            item = h.to_dict()
            item['change_type'] = f"{h.entity_type} {h.action}"
            result.append(item)
        
        return jsonify({
            'history': result
        }), 200
        
    except Exception as e:
        print(f"Error getting version history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

