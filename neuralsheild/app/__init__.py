from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Create instance directory if it doesn't exist
    instance_path = os.path.join(app.root_path, '..', 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance directory: {instance_path}")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Register blueprints
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main_bp)
    
    # Initialize spam detector with app context
    from app.spam_detector import spam_detector
    with app.app_context():
        spam_detector.init_app(app)
    
    # Create database tables and admin user
    with app.app_context():
        db.create_all()
        
        # Import User model inside the app context
        from app.models import User
        
        # Check if admin user exists
        admin_email = app.config.get('ADMIN_EMAIL')
        if admin_email:
            # Use db.session.query() instead of User.query to avoid context issues
            admin_exists = db.session.query(User).filter_by(email=admin_email).first()
            if not admin_exists:
                admin_user = User(
                    username='admin',
                    email=admin_email,
                    is_admin=True
                )
                admin_user.set_password('adminpassword')
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created")
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))