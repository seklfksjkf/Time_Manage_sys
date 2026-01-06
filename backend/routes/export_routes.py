"""
Export API Routes
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.project import Project
from models.task import Task
from models.export_history import ExportHistory
import json
import io

bp = Blueprint('export', __name__)


@bp.route('/projects/<int:project_id>/json', methods=['GET'])
@jwt_required()
def export_project_json(project_id):
    """Export project data as JSON"""
    try:
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get all project data
        tasks = Task.query.filter_by(project_id=project_id).all()
        
        export_data = {
            'project': project.to_dict(include_relations=True),
            'tasks': [t.to_dict(include_relations=True) for t in tasks]
        }
        
        # Log export
        export_record = ExportHistory(
            project_id=project_id,
            user_id=current_user_id,
            export_type='json',
            file_path=f'project_{project_id}_export.json'
        )
        db.session.add(export_record)
        db.session.commit()
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/projects/<int:project_id>/csv', methods=['GET'])
@jwt_required()
def export_project_csv(project_id):
    """Export project tasks as CSV"""
    try:
        current_user_id = int(get_jwt_identity())
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        tasks = Task.query.filter_by(project_id=project_id).all()
        
        # Create CSV content
        csv_lines = ['ID,Title,Start Date,End Date,Status,Priority,Progress,Assigned To']
        
        for task in tasks:
            assignee_name = task.assignee.full_name if task.assignee else 'Unassigned'
            line = f'{task.id},{task.title},{task.start_date},{task.end_date},{task.status},{task.priority},{task.progress},{assignee_name}'
            csv_lines.append(line)
        
        csv_content = '\n'.join(csv_lines)
        
        # Log export
        export_record = ExportHistory(
            project_id=project_id,
            user_id=current_user_id,
            export_type='excel',
            file_path=f'project_{project_id}_export.csv'
        )
        db.session.add(export_record)
        db.session.commit()
        
        # Return CSV as downloadable file
        return csv_content, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=project_{project_id}_tasks.csv'
        }
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/projects/<int:project_id>/report', methods=['GET'])
@jwt_required()
def generate_project_report(project_id):
    """Generate project progress report"""
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        tasks = Task.query.filter_by(project_id=project_id).all()
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == 'completed'])
        in_progress_tasks = len([t for t in tasks if t.status == 'in_progress'])
        pending_tasks = len([t for t in tasks if t.status == 'pending'])
        blocked_tasks = len([t for t in tasks if t.status == 'blocked'])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average progress
        total_progress = sum(t.progress for t in tasks)
        avg_progress = (total_progress / total_tasks) if total_tasks > 0 else 0
        
        # Task breakdown by priority
        priority_breakdown = {
            'low': len([t for t in tasks if t.priority == 'low']),
            'medium': len([t for t in tasks if t.priority == 'medium']),
            'high': len([t for t in tasks if t.priority == 'high']),
            'critical': len([t for t in tasks if t.priority == 'critical'])
        }
        
        report = {
            'project': project.to_dict(include_relations=True),
            'summary': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': pending_tasks,
                'blocked_tasks': blocked_tasks,
                'completion_rate': round(completion_rate, 2),
                'average_progress': round(avg_progress, 2)
            },
            'priority_breakdown': priority_breakdown,
            'tasks': [t.to_dict() for t in tasks]
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/history', methods=['GET'])
@jwt_required()
def get_export_history():
    """Get export history for current user"""
    try:
        current_user_id = int(get_jwt_identity())
        
        history = ExportHistory.query.filter_by(user_id=current_user_id).order_by(
            ExportHistory.created_at.desc()
        ).limit(20).all()
        
        return jsonify({
            'history': [h.to_dict() for h in history]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

