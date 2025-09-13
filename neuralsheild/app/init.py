from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set the correct data directory for the spam detector
    import os
    app.config['MODEL_DATA_DIR'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

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

    # Create database tables
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        from app.models import User
        if not User.query.filter_by(email=app.config['ADMIN_EMAIL']).first():
            admin_user = User(
                username='admin',
                email=app.config['ADMIN_EMAIL'],
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