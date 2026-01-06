"""
Task Dependency Model
"""
from extensions import db
from datetime import datetime


class TaskDependency(db.Model):
    """Task dependency model for managing task relationships"""
    
    __tablename__ = 'task_dependencies'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    depends_on_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    dependency_type = db.Column(db.Enum('finish_to_start', 'start_to_start', 'finish_to_finish', 'start_to_finish'), 
                                default='finish_to_start')
    lag_days = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'depends_on_task_id': self.depends_on_task_id,
            'dependency_type': self.dependency_type,
            'lag_days': self.lag_days,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TaskDependency {self.task_id} depends on {self.depends_on_task_id}>'

