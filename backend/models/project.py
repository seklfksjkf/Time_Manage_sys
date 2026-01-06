"""
Project Model
"""
from extensions import db
from datetime import datetime


class Project(db.Model):
    """Project model for managing projects"""
    
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    deadline = db.Column(db.Date)
    status = db.Column(db.Enum('planning', 'in_progress', 'completed', 'on_hold', 'cancelled'), default='planning')
    color = db.Column(db.String(7), default='#3498db')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    milestones = db.relationship('Milestone', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    members = db.relationship('ProjectMember', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    ai_predictions = db.relationship('AIPrediction', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    exports = db.relationship('ExportHistory', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_relations=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            data['tasks_count'] = self.tasks.count()
            data['members_count'] = self.members.count()
            data['completed_tasks'] = self.tasks.filter_by(status='completed').count()
            
        return data
    
    def __repr__(self):
        return f'<Project {self.name}>'

