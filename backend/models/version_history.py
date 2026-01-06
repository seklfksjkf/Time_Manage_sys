"""
Version History Model
"""
from extensions import db
from datetime import datetime
import json


class VersionHistory(db.Model):
    """Version history model for tracking changes"""
    
    __tablename__ = 'version_history'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.Enum('project', 'task', 'milestone'), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.Enum('created', 'updated', 'deleted'), nullable=False)
    changes = db.Column(db.JSON)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='version_changes')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'changes': self.changes,
            'changed_by': self.changed_by,
            'changed_by_name': self.user.full_name if self.user else None,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }
    
    def __repr__(self):
        return f'<VersionHistory {self.entity_type}:{self.entity_id} {self.action}>'

