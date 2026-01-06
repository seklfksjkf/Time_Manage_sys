"""
AI Prediction Model
"""
from extensions import db
from datetime import datetime


class AIPrediction(db.Model):
    """AI prediction model for smart features"""
    
    __tablename__ = 'ai_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    prediction_type = db.Column(db.Enum('duration_estimate', 'deadline_risk', 'success_probability', 'resource_suggestion'), 
                                nullable=False)
    prediction_data = db.Column(db.JSON, nullable=False)
    confidence_score = db.Column(db.Numeric(3, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'prediction_type': self.prediction_type,
            'prediction_data': self.prediction_data,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AIPrediction {self.prediction_type} for Project {self.project_id}>'

