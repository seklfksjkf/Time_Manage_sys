"""
Flask Extensions
Centralized extension instances to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

