"""
Task Model
"""
from extensions import db
from datetime import datetime


class Task(db.Model):
    """Task model for managing tasks"""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    estimated_duration = db.Column(db.Integer)  # in days
    actual_duration = db.Column(db.Integer)  # in days
    progress = db.Column(db.Integer, default=0)  # 0-100
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', 'blocked'), default='pending')
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    color = db.Column(db.String(7))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dependencies = db.relationship('TaskDependency',
                                  foreign_keys='TaskDependency.task_id',
                                  backref='task',
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')
    dependents = db.relationship('TaskDependency',
                                foreign_keys='TaskDependency.depends_on_task_id',
                                backref='depends_on_task',
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('TaskComment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    task_assignments = db.relationship('TaskAssignment', backref='task', lazy='dynamic',
                                       cascade='all, delete-orphan')
    
    def to_dict(self, include_relations=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'progress': self.progress,
            'status': self.status,
            'priority': self.priority,
            'color': self.color,
            'assigned_to': self.assigned_to,
            'assigned_to_name': self.assignee.full_name if self.assignee else None,
            'assignees': [ta.to_dict() for ta in self.task_assignments.all()],
            'assigned_to_names': [ta.user.full_name for ta in self.task_assignments.all() if ta.user],
            'created_by': self.created_by,
            'created_by_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data['dependencies'] = [dep.depends_on_task_id for dep in self.dependencies]
            data['comments_count'] = self.comments.count()
            
        return data
    
    def __repr__(self):
        return f'<Task {self.title}>'

