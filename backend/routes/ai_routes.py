"""AI / Smart suggestion API Routes

Heuristic/Statistics based suggestions (no external LLM required)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

from extensions import db
from models.task import Task
from models.project import Project
from models.project_member import ProjectMember
from models.user import User
from models.notification import Notification

bp = Blueprint('ai', __name__)


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
    except Exception:
        return None


@bp.route('/task-duration', methods=['GET'])
@jwt_required()
def suggest_task_duration():
    """Suggest task estimated duration (days) based on historical tasks."""
    try:
        project_id = request.args.get('project_id', type=int)
        title = request.args.get('title', type=str) or ''
        priority = request.args.get('priority', type=str)

        if not project_id:
            return jsonify({'error': 'project_id is required'}), 400

        # Base query: completed tasks with actual_duration
        q = Task.query.filter(
            Task.project_id == project_id,
            Task.actual_duration.isnot(None)
        )

        if priority:
            q = q.filter(Task.priority == priority)

        tasks = q.order_by(Task.updated_at.desc()).limit(50).all()

        durations = [t.actual_duration for t in tasks if isinstance(t.actual_duration, int) and t.actual_duration > 0]

        # Fallback defaults by priority
        defaults = {
            'low': 1,
            'medium': 3,
            'high': 5,
            'critical': 7
        }

        if durations:
            avg = sum(durations) / len(durations)
            # Light adjustment: longer titles often represent bigger tasks
            title_bonus = 0
            if len(title.strip()) >= 20:
                title_bonus = 1
            suggested = max(1, int(round(avg + title_bonus)))
            return jsonify({
                'suggested_days': suggested,
                'basis_count': len(durations),
                'priority': priority,
                'title': title
            }), 200

        return jsonify({
            'suggested_days': defaults.get(priority, 3),
            'basis_count': 0,
            'priority': priority,
            'title': title
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/resource-suggestions', methods=['GET'])
@jwt_required()
def suggest_resources():
    """Suggest assignees based on current workload within a project."""
    try:
        project_id = request.args.get('project_id', type=int)
        start_date = _parse_date(request.args.get('start_date'))
        end_date = _parse_date(request.args.get('end_date'))

        if not project_id:
            return jsonify({'error': 'project_id is required'}), 400

        # Load project members
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        member_user_ids = [m.user_id for m in members]

        if not member_user_ids:
            return jsonify({'suggestions': []}), 200

        # Workload: count active tasks overlapping provided window (or all active tasks)
        task_q = Task.query.filter(
            Task.project_id == project_id,
            Task.status.in_(['pending', 'in_progress', 'blocked'])
        )
        if start_date and end_date:
            task_q = task_q.filter(Task.start_date <= end_date, Task.end_date >= start_date)

        active_tasks = task_q.all()

        # Collect assignments
        workload = {uid: 0 for uid in member_user_ids}
        for t in active_tasks:
            # multi-assignments
            for ta in t.task_assignments.all():
                if ta.user_id in workload:
                    workload[ta.user_id] += 1
            # legacy single assignment
            if t.assigned_to and t.assigned_to in workload:
                workload[t.assigned_to] += 1

        users = User.query.filter(User.id.in_(member_user_ids)).all()
        user_map = {u.id: u for u in users}

        suggestions = []
        for uid in member_user_ids:
            u = user_map.get(uid)
            if not u:
                continue
            suggestions.append({
                'user_id': uid,
                'user_name': u.full_name or u.username,
                'workload': workload.get(uid, 0)
            })

        suggestions.sort(key=lambda x: (x['workload'], x['user_name']))

        return jsonify({'suggestions': suggestions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/deadline-risk-scan', methods=['POST'])
@jwt_required()
def deadline_risk_scan():
    """Scan a project tasks and create deadline risk notifications."""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        project_id = data.get('project_id')
        if not project_id:
            return jsonify({'error': 'project_id is required'}), 400

        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Permission: allow project owner or admin; otherwise must be a project member
        user = User.query.get(current_user_id)
        is_admin = bool(user and getattr(user, 'role', None) == 'admin')
        is_owner = current_user_id == project.owner_id

        if not (is_admin or is_owner):
            membership = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user_id).first()
            if not membership:
                return jsonify({'error': 'Permission denied'}), 403

        tasks = Task.query.filter(
            Task.project_id == project_id,
            Task.status.in_(['pending', 'in_progress', 'blocked'])
        ).all()

        created = 0
        now = datetime.utcnow().date()

        for t in tasks:
            if not t.end_date or not t.start_date:
                continue

            total_days = max(1, (t.end_date - t.start_date).days)
            elapsed_days = max(0, (now - t.start_date).days)
            time_ratio = min(1.0, elapsed_days / total_days)
            expected_progress = int(round(time_ratio * 100))

            progress = t.progress or 0
            days_left = (t.end_date - now).days

            # Risk heuristic
            risk = 0
            if days_left <= 0 and progress < 100:
                risk = 100
            elif days_left <= 2 and progress < 80:
                risk = 80
            elif progress + 10 < expected_progress:
                risk = 60

            if risk < 60:
                continue

            title = 'Deadline Risk Alert'
            message = f'Task "{t.title}" may miss the deadline. Progress {progress}%, expected ~{expected_progress}%. Due in {days_left} day(s).'

            # Notify all assignees (multi + legacy)
            target_user_ids = set()
            for ta in t.task_assignments.all():
                target_user_ids.add(ta.user_id)
            if t.assigned_to:
                target_user_ids.add(t.assigned_to)

            # If no assignee, notify project owner
            if not target_user_ids:
                target_user_ids.add(project.owner_id)

            for uid in target_user_ids:
                # avoid duplicate unread alerts for same task
                existing = Notification.query.filter_by(
                    user_id=uid,
                    type='deadline_alert',
                    related_entity_type='task',
                    related_entity_id=t.id,
                    is_read=False
                ).first()
                if existing:
                    continue

                n = Notification(
                    user_id=uid,
                    type='deadline_alert',
                    title=title,
                    message=message,
                    related_entity_type='task',
                    related_entity_id=t.id
                )
                db.session.add(n)
                created += 1

        db.session.commit()

        return jsonify({
            'message': 'Risk scan completed',
            'notifications_created': created
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
