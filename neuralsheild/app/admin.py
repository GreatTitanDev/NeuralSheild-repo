from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, AnalysisHistory, ContactMessage, ModelTrainingLog
from app.spam_detector import spam_detector
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('main.home'))

@admin_bp.route('/')
def dashboard():
    # Get stats for dashboard
    total_users = User.query.count()
    total_analyses = AnalysisHistory.query.count()
    total_contacts = ContactMessage.query.count()
    recent_analyses = AnalysisHistory.query.order_by(AnalysisHistory.created_at.desc()).limit(10).all()
    
    # Get analytics for the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # User growth
    user_growth = User.query.filter(User.created_at >= seven_days_ago).count()
    
    # Analysis stats
    analysis_stats = db.session.query(
        AnalysisHistory.prediction,
        db.func.count(AnalysisHistory.id)
    ).filter(AnalysisHistory.created_at >= seven_days_ago).group_by(AnalysisHistory.prediction).all()
    
    spam_count = next((count for pred, count in analysis_stats if pred == 'spam'), 0)
    ham_count = next((count for pred, count in analysis_stats if pred == 'ham'), 0)
    
    # Platform distribution
    platform_stats = db.session.query(
        AnalysisHistory.platform,
        db.func.count(AnalysisHistory.id)
    ).filter(AnalysisHistory.created_at >= seven_days_ago).group_by(AnalysisHistory.platform).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_analyses=total_analyses,
                         total_contacts=total_contacts,
                         user_growth=user_growth,
                         spam_count=spam_count,
                         ham_count=ham_count,
                         platform_stats=platform_stats,
                         recent_analyses=recent_analyses)

@admin_bp.route('/users')
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/analyses')
def analyses():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    analyses = AnalysisHistory.query.order_by(
        AnalysisHistory.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/analyses.html', analyses=analyses)

@admin_bp.route('/contacts')
def contacts():
    contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)

@admin_bp.route('/model')
def model_management():
    training_logs = ModelTrainingLog.query.order_by(ModelTrainingLog.training_date.desc()).all()
    return render_template('admin/model.html', training_logs=training_logs)

@admin_bp.route('/train-model', methods=['POST'])
def train_model():
    try:
        # Create training log
        training_log = ModelTrainingLog(status='in_progress', notes='Training initiated by admin')
        db.session.add(training_log)
        db.session.commit()
        
        # Train model (this could be done in a background task)
        accuracy, precision, recall, f1 = spam_detector.train()
        
        # Update training log
        training_log.status = 'success'
        training_log.accuracy = accuracy
        training_log.precision = precision
        training_log.recall = recall
        training_log.f1_score = f1
        training_log.training_samples = len(spam_detector.combined_df) if hasattr(spam_detector, 'combined_df') else 0
        training_log.notes = 'Model training completed successfully'
        
        db.session.commit()
        
        flash('Model trained successfully!', 'success')
        return jsonify({'success': True, 'accuracy': accuracy})
    
    except Exception as e:
        if 'training_log' in locals():
            training_log.status = 'failed'
            training_log.notes = f'Training failed: {str(e)}'
            db.session.commit()
        
        flash(f'Model training failed: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    action = "activated" if user.is_active else "deactivated"
    flash(f'User {user.username} has been {action}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/contact/<int:contact_id>/read', methods=['POST'])
def mark_contact_read(contact_id):
    contact = ContactMessage.query.get_or_404(contact_id)
    contact.is_read = True
    db.session.commit()
    
    flash('Contact marked as read.', 'success')
    return redirect(url_for('admin.contacts'))

@admin_bp.route('/stats')
def get_stats():
    # Get statistics for charts
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # User registrations by day
    user_registrations = db.session.query(
        db.func.date(User.created_at),
        db.func.count(User.id)
    ).filter(User.created_at >= start_date).group_by(db.func.date(User.created_at)).all()
    
    # Analyses by day and type
    analysis_stats = db.session.query(
        db.func.date(AnalysisHistory.created_at),
        AnalysisHistory.prediction,
        db.func.count(AnalysisHistory.id)
    ).filter(AnalysisHistory.created_at >= start_date).group_by(
        db.func.date(AnalysisHistory.created_at), AnalysisHistory.prediction
    ).all()
    
    # Format data for charts
    user_data = [{'date': date.strftime('%Y-%m-%d'), 'count': count} for date, count in user_registrations]
    
    spam_data = []
    ham_data = []
    
    for date, prediction, count in analysis_stats:
        date_str = date.strftime('%Y-%m-%d')
        if prediction == 'spam':
            spam_data.append({'date': date_str, 'count': count})
        else:
            ham_data.append({'date': date_str, 'count': count})
    
    return jsonify({
        'users': user_data,
        'spam': spam_data,
        'ham': ham_data
    })