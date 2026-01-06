"""
Milestone API Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.milestone import Milestone
from models.notification import Notification
from models.version_history import VersionHistory
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import parse_datetime

bp = Blueprint('milestones', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def list_milestones():
    """List milestones (optionally filtered by project)"""
    try:
        project_id = request.args.get('project_id', type=int)
        
        query = Milestone.query
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        milestones = query.order_by(Milestone.date).all()
        
        return jsonify({
            'milestones': [m.to_dict() for m in milestones]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_milestone():
    """Create new milestone"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation
        required_fields = ['project_id', 'name', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        milestone = Milestone(
            project_id=data['project_id'],
            name=data['name'],
            description=data.get('description'),
            date=parse_datetime(data.get('date')).date() if data.get('date') else None,
            status=data.get('status', 'upcoming'),
            color=data.get('color', '#e74c3c')
        )
        
        db.session.add(milestone)
        db.session.flush()
        
        # Log version history
        history = VersionHistory(
            entity_type='milestone',
            entity_id=milestone.id,
            action='created',
            changed_by=current_user_id,
            changes={'name': milestone.name}
        )
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Milestone created successfully',
            'milestone': milestone.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:milestone_id>', methods=['GET'])
@jwt_required()
def get_milestone(milestone_id):
    """Get milestone details"""
    try:
        milestone = Milestone.query.get(milestone_id)
        
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        
        return jsonify({
            'milestone': milestone.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:milestone_id>', methods=['PUT'])
@jwt_required()
def update_milestone(milestone_id):
    """Update milestone"""
    try:
        current_user_id = int(get_jwt_identity())
        milestone = Milestone.query.get(milestone_id)
        
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        
        data = request.get_json()
        old_values = {}
        
        if 'name' in data:
            old_values['name'] = milestone.name
            milestone.name = data['name']
        if 'description' in data:
            milestone.description = data['description']
        if 'date' in data:
            old_values['date'] = milestone.date.isoformat()
            parsed_date = parse_datetime(data.get('date'))
            milestone.date = parsed_date.date() if parsed_date else None
        if 'status' in data:
            old_values['status'] = milestone.status
            milestone.status = data['status']
        if 'color' in data:
            milestone.color = data['color']
        
        # Log version history
        if old_values:
            history = VersionHistory(
                entity_type='milestone',
                entity_id=milestone_id,
                action='updated',
                changed_by=current_user_id,
                changes=old_values
            )
            db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Milestone updated successfully',
            'milestone': milestone.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:milestone_id>', methods=['DELETE'])
@jwt_required()
def delete_milestone(milestone_id):
    """Delete milestone"""
    try:
        current_user_id = int(get_jwt_identity())
        milestone = Milestone.query.get(milestone_id)
        
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        
        # Log version history
        history = VersionHistory(
            entity_type='milestone',
            entity_id=milestone_id,
            action='deleted',
            changed_by=current_user_id,
            changes={'name': milestone.name}
        )
        db.session.add(history)
        
        db.session.delete(milestone)
        db.session.commit()
        
        return jsonify({
            'message': 'Milestone deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

