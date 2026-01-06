"""
Time Management System - Flask Backend Application
Main entry point for the Flask REST API
"""
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import timedelta
import sys
import os

# Add parent directory to path to import database config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.config import DatabaseConfig

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = DatabaseConfig.SQLALCHEMY_ECHO
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Initialize extensions with app
    from extensions import db, jwt
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # JWT error handlers (must be inside create_app)
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired tokens"""
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please login again'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid tokens"""
        print(f"❌ Invalid token error: {error}")
        return jsonify({
            'error': 'Invalid token',
            'message': 'Token verification failed'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing tokens"""
        print(f"❌ Missing token error: {error}")
        return jsonify({
            'error': 'Authorization required',
            'message': 'No token provided'
        }), 401
    
    # Import and register blueprints
    from routes import auth_routes, project_routes, task_routes, timeline_routes
    from routes import milestone_routes, notification_routes, dashboard_routes, export_routes
    
    app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
    app.register_blueprint(project_routes.bp, url_prefix='/api/projects')
    app.register_blueprint(task_routes.bp, url_prefix='/api/tasks')
    app.register_blueprint(timeline_routes.bp, url_prefix='/api/timeline')
    app.register_blueprint(milestone_routes.bp, url_prefix='/api/milestones')
    app.register_blueprint(notification_routes.bp, url_prefix='/api/notifications')
    app.register_blueprint(dashboard_routes.bp, url_prefix='/api/dashboard')
    app.register_blueprint(export_routes.bp, url_prefix='/api/export')
    
    return app

# Create app instance
app = create_app()

# Import db for use in other modules
from extensions import db, jwt

# Root route
@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'name': 'Time Management System API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': '/api/auth',
            'projects': '/api/projects',
            'tasks': '/api/tasks',
            'timeline': '/api/timeline',
            'milestones': '/api/milestones',
            'notifications': '/api/notifications',
            'dashboard': '/api/dashboard',
            'export': '/api/export'
        }
    })

# Health check endpoint
@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred'
    }), 500

# JWT error handlers are now inside create_app() function


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"\n{'='*60}")
    print("Time Management System API Server")
    print(f"{'='*60}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"Running on: http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug)

