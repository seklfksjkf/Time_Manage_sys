"""
Task Assignment Model - Many-to-Many relationship between tasks and users
"""
from extensions import db
from datetime import datetime


class TaskAssignment(db.Model):
    """Task assignment model for multiple assignees"""
    
    __tablename__ = 'task_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='task_assignments')
    assigned_by_user = db.relationship('User', foreign_keys=[assigned_by])
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        db.UniqueConstraint('task_id', 'user_id', name='unique_task_assignment'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'assigned_by': self.assigned_by
        }
    
    def __repr__(self):
        return f'<TaskAssignment task={self.task_id} user={self.user_id}>'
