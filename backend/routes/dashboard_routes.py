"""
Dashboard API Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import get_current_user_id
from models.project import Project
from models.task import Task
from models.project_member import ProjectMember
from models.notification import Notification
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)


@bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Get dashboard overview statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Get all user's projects (owned + member)
        owned_project_ids = [p.id for p in Project.query.filter_by(owner_id=current_user_id).all()]
        member_project_ids = [pm.project_id for pm in ProjectMember.query.filter_by(user_id=current_user_id).all()]
        all_project_ids = list(set(owned_project_ids + member_project_ids))
        
        # Get projects count by status
        if all_project_ids:
            planning_count = Project.query.filter(Project.id.in_(all_project_ids), Project.status == 'planning').count()
            in_progress_count = Project.query.filter(Project.id.in_(all_project_ids), Project.status == 'in_progress').count()
            on_hold_count = Project.query.filter(Project.id.in_(all_project_ids), Project.status == 'on_hold').count()
            completed_count = Project.query.filter(Project.id.in_(all_project_ids), Project.status == 'completed').count()
        else:
            planning_count = in_progress_count = on_hold_count = completed_count = 0
        
        total_projects = len(all_project_ids)
        
        # Get tasks count
        total_tasks = Task.query.filter_by(assigned_to=current_user_id).count()
        pending_tasks = Task.query.filter_by(assigned_to=current_user_id, status='pending').count()
        in_progress_tasks = Task.query.filter_by(assigned_to=current_user_id, status='in_progress').count()
        completed_tasks = Task.query.filter_by(assigned_to=current_user_id, status='completed').count()
        
        # Get upcoming deadlines (next 7 days)
        today = datetime.utcnow().date()
        next_week = today + timedelta(days=7)
        
        upcoming_tasks = Task.query.filter(
            Task.assigned_to == current_user_id,
            Task.end_date >= today,
            Task.end_date <= next_week,
            Task.status != 'completed'
        ).order_by(Task.end_date).limit(5).all()
        
        # Get recent projects
        recent_projects_query = Project.query.filter_by(owner_id=current_user_id).order_by(
            Project.updated_at.desc()
        ).limit(5)
        
        recent_projects = recent_projects_query.all()
        
        # Get unread notifications count
        unread_notifications = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).count()
        
        return jsonify({
            'projects': {
                'total': total_projects,
                'planning': planning_count,
                'in_progress': in_progress_count,
                'on_hold': on_hold_count,
                'completed': completed_count
            },
            'tasks': {
                'total': total_tasks,
                'pending': pending_tasks,
                'in_progress': in_progress_tasks,
                'completed': completed_tasks
            },
            'upcoming_tasks': [t.to_dict() for t in upcoming_tasks],
            'recent_projects': [p.to_dict(include_relations=True) for p in recent_projects],
            'unread_notifications': unread_notifications
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    """Get all tasks assigned to current user"""
    try:
        current_user_id = int(get_jwt_identity())
        status = request.args.get('status')
        
        query = Task.query.filter_by(assigned_to=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        tasks = query.order_by(Task.end_date).all()
        
        return jsonify({
            'tasks': [t.to_dict(include_relations=True) for t in tasks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get detailed statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Task completion rate
        total_tasks = Task.query.filter_by(assigned_to=current_user_id).count()
        completed_tasks = Task.query.filter_by(assigned_to=current_user_id, status='completed').count()
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Tasks by priority
        tasks_by_priority = db.session.query(
            Task.priority,
            func.count(Task.id)
        ).filter_by(assigned_to=current_user_id).group_by(Task.priority).all()
        
        priority_stats = {priority: count for priority, count in tasks_by_priority}
        
        # Projects by status
        projects_by_status = db.session.query(
            Project.status,
            func.count(Project.id)
        ).filter_by(owner_id=current_user_id).group_by(Project.status).all()
        
        project_stats = {status: count for status, count in projects_by_status}
        
        return jsonify({
            'completion_rate': round(completion_rate, 2),
            'tasks_by_priority': priority_stats,
            'projects_by_status': project_stats,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

