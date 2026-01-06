"""
Timeline/Gantt Chart API Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.task import Task
from models.task_dependency import TaskDependency
from models.milestone import Milestone
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import parse_datetime

bp = Blueprint('timeline', __name__)


@bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_timeline(project_id):
    """Get Gantt chart data for a project"""
    try:
        # Get all tasks for the project
        tasks = Task.query.filter_by(project_id=project_id).order_by(Task.start_date).all()
        
        # Get all milestones
        milestones = Milestone.query.filter_by(project_id=project_id).order_by(Milestone.date).all()
        
        # Get all dependencies
        task_ids = [t.id for t in tasks]
        dependencies = TaskDependency.query.filter(TaskDependency.task_id.in_(task_ids)).all()
        
        # Format for Gantt chart
        gantt_tasks = []
        for task in tasks:
            # Skip tasks without dates
            if not task.start_date or not task.end_date:
                continue
                
            gantt_task = {
                'id': task.id,
                'title': task.title,  # Changed from 'name' to 'title' for consistency
                'start_date': task.start_date.isoformat(),
                'end_date': task.end_date.isoformat(),
                'progress': task.progress or 0,
                'status': task.status,
                'priority': task.priority,
                'color': task.color,
                'assigned_to': task.assigned_to,
                'assigned_to_name': task.assignee.full_name if task.assignee else None,
                'dependencies': [d.depends_on_task_id for d in task.dependencies]
            }
            gantt_tasks.append(gantt_task)
        
        # Format milestones
        gantt_milestones = []
        for milestone in milestones:
            gantt_milestone = {
                'id': milestone.id,
                'name': milestone.name,
                'date': milestone.date.isoformat(),
                'status': milestone.status,
                'color': milestone.color,
                'type': 'milestone'
            }
            gantt_milestones.append(gantt_milestone)
        
        return jsonify({
            'tasks': gantt_tasks,
            'milestones': gantt_milestones,
            'dependencies': [d.to_dict() for d in dependencies]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tasks/<int:task_id>/move', methods=['PUT'])
@jwt_required()
def move_task(task_id):
    """Update task dates (for drag-and-drop)"""
    try:
        current_user_id = int(get_jwt_identity())
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        if 'start_date' in data:
            parsed_date = parse_datetime(data.get('start_date'))
            task.start_date = parsed_date.date() if parsed_date else None
        if 'end_date' in data:
            parsed_date = parse_datetime(data.get('end_date'))
            task.end_date = parsed_date.date() if parsed_date else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task moved successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/projects/<int:project_id>/critical-path', methods=['GET'])
@jwt_required()
def get_critical_path(project_id):
    """Calculate and return critical path for project"""
    try:
        # Get all tasks
        tasks = Task.query.filter_by(project_id=project_id).all()
        
        # Simple critical path calculation (tasks without slack time)
        # In a real application, use more sophisticated algorithms
        critical_tasks = []
        
        for task in tasks:
            # Check if task has dependents
            dependents = TaskDependency.query.filter_by(depends_on_task_id=task.id).all()
            
            if dependents or task.priority == 'critical':
                critical_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'start_date': task.start_date.isoformat(),
                    'end_date': task.end_date.isoformat(),
                    'status': task.status
                })
        
        return jsonify({
            'critical_path': critical_tasks
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/projects/<int:project_id>/progress', methods=['GET'])
@jwt_required()
def get_project_progress(project_id):
    """Get overall project progress"""
    try:
        tasks = Task.query.filter_by(project_id=project_id).all()
        
        if not tasks:
            return jsonify({'progress': 0, 'tasks_summary': {}}), 200
        
        total_progress = sum(task.progress for task in tasks)
        avg_progress = total_progress / len(tasks)
        
        status_summary = {
            'pending': len([t for t in tasks if t.status == 'pending']),
            'in_progress': len([t for t in tasks if t.status == 'in_progress']),
            'completed': len([t for t in tasks if t.status == 'completed']),
            'blocked': len([t for t in tasks if t.status == 'blocked'])
        }
        
        return jsonify({
            'progress': round(avg_progress, 2),
            'total_tasks': len(tasks),
            'tasks_summary': status_summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

