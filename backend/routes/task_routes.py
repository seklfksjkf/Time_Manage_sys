"""
Task Management API Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.task import Task
from models.task_dependency import TaskDependency
from models.task_comment import TaskComment
from models.task_assignment import TaskAssignment
from models.project_member import ProjectMember
from models.notification import Notification
from models.version_history import VersionHistory
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import parse_datetime

bp = Blueprint('tasks', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def list_tasks():
    """List tasks (optionally filtered by project)"""
    try:
        project_id = request.args.get('project_id', type=int)
        status = request.args.get('status')
        assigned_to = request.args.get('assigned_to', type=int)
        
        query = Task.query
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        if status:
            query = query.filter_by(status=status)
        if assigned_to:
            query = query.filter_by(assigned_to=assigned_to)
        
        tasks = query.order_by(Task.start_date).all()
        
        return jsonify({
            'tasks': [t.to_dict(include_relations=True) for t in tasks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create new task"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation
        required_fields = ['project_id', 'title', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Handle assigned_to - if list, set to None (use TaskAssignment instead)
        assigned_to = data.get('assigned_to')
        if isinstance(assigned_to, list):
            assigned_to = None  # Multiple assignees handled via TaskAssignment

        # Create task
        task = Task(
            project_id=data['project_id'],
            title=data['title'],
            description=data.get('description'),
            start_date=parse_datetime(data.get('start_date')).date() if data.get('start_date') else None,
            end_date=parse_datetime(data.get('end_date')).date() if data.get('end_date') else None,
            estimated_duration=data.get('estimated_duration'),
            progress=data.get('progress', 0),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            color=data.get('color'),
            assigned_to=assigned_to,
            created_by=current_user_id
        )
        
        db.session.add(task)
        db.session.flush()
        
        # Handle array of assignees (for multiple assignees support)
        assignees = data.get('assigned_to')
        if assignees:
            if isinstance(assignees, list):
                # Multiple assignees - create TaskAssignment records
                for user_id in assignees:
                    assignment = TaskAssignment(
                        task_id=task.id,
                        user_id=user_id,
                        assigned_by=current_user_id
                    )
                    db.session.add(assignment)
                    # Create notification for each assignee
                    if user_id != current_user_id:
                        notification = Notification(
                            user_id=user_id,
                            type='task_assigned',
                            title='New Task Assigned',
                            message=f'You have been assigned to task: {task.title}',
                            related_entity_type='task',
                            related_entity_id=task.id
                        )
                        db.session.add(notification)
            else:
                # Single assignee (backward compatibility)
                task.assigned_to = assignees
                if assignees != current_user_id:
                    notification = Notification(
                        user_id=assignees,
                        type='task_assigned',
                        title='New Task Assigned',
                        message=f'You have been assigned to task: {task.title}',
                        related_entity_type='task',
                        related_entity_id=task.id
                    )
                    db.session.add(notification)
        
        # Log version history
        history = VersionHistory(
            entity_type='task',
            entity_id=task.id,
            action='created',
            changed_by=current_user_id,
            changes={'title': task.title}
        )
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict(include_relations=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get task details"""
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({
            'task': task.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update task"""
    try:
        current_user_id = int(get_jwt_identity())
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        old_values = {}
        old_assignee = task.assigned_to
        
        # Update fields
        if 'title' in data:
            old_values['title'] = task.title
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'start_date' in data:
            parsed_date = parse_datetime(data.get('start_date'))
            task.start_date = parsed_date.date() if parsed_date else None
        if 'end_date' in data:
            parsed_date = parse_datetime(data.get('end_date'))
            task.end_date = parsed_date.date() if parsed_date else None
        if 'estimated_duration' in data:
            task.estimated_duration = data['estimated_duration']
        if 'actual_duration' in data:
            task.actual_duration = data['actual_duration']
        if 'progress' in data:
            old_values['progress'] = task.progress
            task.progress = data['progress']
        if 'status' in data:
            old_values['status'] = task.status
            task.status = data['status']
        if 'priority' in data:
            old_values['priority'] = task.priority
            task.priority = data['priority']
        if 'color' in data:
            task.color = data['color']
        if 'assigned_to' in data:
            new_assignees = data['assigned_to']
            if isinstance(new_assignees, list):
                # Multiple assignees - update TaskAssignment records
                old_assignees = set(ta.user_id for ta in task.task_assignments)
                new_assignees_set = set(new_assignees)
                
                # Remove assignments that are no longer needed
                for ta in task.task_assignments:
                    if ta.user_id not in new_assignees_set:
                        db.session.delete(ta)
                
                # Add new assignments
                for user_id in new_assignees:
                    if user_id not in old_assignees:
                        assignment = TaskAssignment(
                            task_id=task.id,
                            user_id=user_id,
                            assigned_by=current_user_id
                        )
                        db.session.add(assignment)
                        # Create notification for new assignee
                        if user_id != current_user_id:
                            notification = Notification(
                                user_id=user_id,
                                type='task_assigned',
                                title='Task Reassigned',
                                message=f'You have been assigned to task: {task.title}',
                                related_entity_type='task',
                                related_entity_id=task.id
                            )
                            db.session.add(notification)
                
                old_values['assigned_to'] = list(old_assignees)
            else:
                # Single assignee (backward compatibility)
                old_values['assigned_to'] = task.assigned_to
                task.assigned_to = new_assignees
                
                # Create notification for new assignee
                if new_assignees and new_assignees != old_assignee:
                    notification = Notification(
                        user_id=new_assignees,
                        type='task_assigned',
                        title='Task Reassigned',
                        message=f'You have been assigned to task: {task.title}',
                        related_entity_type='task',
                        related_entity_id=task.id
                    )
                    db.session.add(notification)
        
        # Log version history
        if old_values:
            history = VersionHistory(
                entity_type='task',
                entity_id=task_id,
                action='updated',
                changed_by=current_user_id,
                changes=old_values
            )
            db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete task"""
    try:
        current_user_id = int(get_jwt_identity())
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Log version history
        history = VersionHistory(
            entity_type='task',
            entity_id=task_id,
            action='deleted',
            changed_by=current_user_id,
            changes={'title': task.title}
        )
        db.session.add(history)
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>/dependencies', methods=['GET'])
@jwt_required()
def get_task_dependencies(task_id):
    """Get task dependencies"""
    try:
        dependencies = TaskDependency.query.filter_by(task_id=task_id).all()
        
        return jsonify({
            'dependencies': [d.to_dict() for d in dependencies]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>/dependencies', methods=['POST'])
@jwt_required()
def add_task_dependency(task_id):
    """Add task dependency"""
    try:
        data = request.get_json()
        
        if 'depends_on_task_id' not in data:
            return jsonify({'error': 'depends_on_task_id is required'}), 400
        
        # Check if dependency already exists
        existing = TaskDependency.query.filter_by(
            task_id=task_id,
            depends_on_task_id=data['depends_on_task_id']
        ).first()
        
        if existing:
            return jsonify({'error': 'Dependency already exists'}), 409
        
        # Create dependency
        dependency = TaskDependency(
            task_id=task_id,
            depends_on_task_id=data['depends_on_task_id'],
            dependency_type=data.get('dependency_type', 'finish_to_start'),
            lag_days=data.get('lag_days', 0)
        )
        
        db.session.add(dependency)
        db.session.commit()
        
        return jsonify({
            'message': 'Dependency added successfully',
            'dependency': dependency.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>/dependencies/<int:dependency_id>', methods=['DELETE'])
@jwt_required()
def remove_task_dependency(task_id, dependency_id):
    """Remove task dependency"""
    try:
        dependency = TaskDependency.query.get(dependency_id)
        
        if not dependency or dependency.task_id != task_id:
            return jsonify({'error': 'Dependency not found'}), 404
        
        db.session.delete(dependency)
        db.session.commit()
        
        return jsonify({
            'message': 'Dependency removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>/comments', methods=['GET'])
@jwt_required()
def get_task_comments(task_id):
    """Get task comments"""
    try:
        comments = TaskComment.query.filter_by(task_id=task_id).order_by(TaskComment.created_at.desc()).all()
        
        return jsonify({
            'comments': [c.to_dict() for c in comments]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def add_task_comment(task_id):
    """Add task comment"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if 'comment' not in data:
            return jsonify({'error': 'Comment text is required'}), 400
        
        comment = TaskComment(
            task_id=task_id,
            user_id=current_user_id,
            comment=data['comment']
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>/comments/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_task_comment(task_id, comment_id):
    """Update task comment"""
    try:
        current_user_id = int(get_jwt_identity())
        comment = TaskComment.query.get(comment_id)
        
        if not comment or comment.task_id != task_id:
            return jsonify({'error': 'Comment not found'}), 404
        
        if comment.user_id != current_user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        if 'comment' in data:
            comment.comment = data['comment']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Comment updated successfully',
            'comment': comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:task_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_task_comment(task_id, comment_id):
    """Delete task comment"""
    try:
        current_user_id = int(get_jwt_identity())
        comment = TaskComment.query.get(comment_id)
        
        if not comment or comment.task_id != task_id:
            return jsonify({'error': 'Comment not found'}), 404
        
        if comment.user_id != current_user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

