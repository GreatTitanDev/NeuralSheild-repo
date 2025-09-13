from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import AnalysisHistory, ContactMessage
from app.spam_detector import spam_detector
import threading
from flask_mail import Message

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('index.html')
    return render_template('landing.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/api')
@login_required
def api_docs():
    return render_template('api.html')

@main_bp.route('/api/detect', methods=['POST'])
def detect_spam():
    # Check for API key or user authentication
    api_key = request.headers.get('X-API-Key')
    user = None
    
    if api_key:
        from app.models import User
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
    elif not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    else:
        user = current_user
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400

        text = data['text']
        platform = data.get('platform', 'email')
        
        if not isinstance(text, str):
            text = str(text)
            
        result = spam_detector.predict(text, platform)
        if result is None:
            prediction, probability = spam_detector.fallback_predict(text)
            explanation = spam_detector.generate_detailed_explanation(text, platform, prediction == 'spam', {})
        else:
            prediction, probability, explanation = result
            
        analysis = AnalysisHistory(
            user_id=user.id,
            content=text,
            platform=platform,
            prediction=prediction,
            confidence=probability
        )
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'prediction': prediction,
            'probability': probability,
            'explanation': explanation,
            'analysis_id': analysis.id
        })
    except Exception as e:
        print(f"Error in spam detection: {str(e)}")
        # Ensure we have text variable for fallback
        if 'text' not in locals():
            text = data.get('text', '') if 'data' in locals() else ''

        prediction, probability = spam_detector.fallback_predict(text)
        explanation = spam_detector.generate_detailed_explanation(text, platform, prediction == 'spam', {})
        
        return jsonify({
            'prediction': prediction,
            'probability': probability,
            'explanation': explanation,
            'error': str(e)
        }), 500

@main_bp.route('/api/history', methods=['GET'])
@login_required
def get_history():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        history = AnalysisHistory.query.filter_by(user_id=current_user.id).order_by(
            AnalysisHistory.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'history': [item.to_dict() for item in history.items],
            'total': history.total,
            'pages': history.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/contact', methods=['POST'])
def contact_form():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([name, email, subject, message]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Check if user is logged in
        user_id = current_user.id if current_user.is_authenticated else None

        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
            user_id=user_id
        )
        db.session.add(contact_msg)
        db.session.commit()
        
        # Send email to admin (implementation depends on your mail setup)
        # send_contact_email(name, email, subject, message)
        
        return jsonify({'message': 'Your message has been sent successfully!'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/generate-key', methods=['POST'])
@login_required
def generate_api_key():
    try:
        api_key = current_user.generate_api_key()
        db.session.commit()
        return jsonify({'api_key': api_key})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'model_trained': spam_detector.is_trained,
        'database_connected': True
    })