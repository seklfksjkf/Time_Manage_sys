"""
Export History Model
"""
from extensions import db
from datetime import datetime


class ExportHistory(db.Model):
    """Export history model for tracking exports"""
    
    __tablename__ = 'export_history'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    export_type = db.Column(db.Enum('pdf', 'png', 'excel'), nullable=False)
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='exports')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else None,
            'export_type': self.export_type,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<ExportHistory {self.export_type} for Project {self.project_id}>'

