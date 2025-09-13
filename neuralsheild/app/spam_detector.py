'''
Enhanced Spam detector module with more analysis methods
'''
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
import json
import urllib.parse
from textblob import TextBlob
#import language_tool_python

class EnhancedSpamDetector:
    """
    Advanced spam detection system with multiple analysis methods
    """
    
    def __init__(self, data_dir=None):
        self.is_trained = False
        self.model = None
        self.preprocessor = None
        
        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
            
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self._create_sample_data()
        
        try:
            self._load_training_data()
            self._build_model()  # Build the model first
            self.train()  # Then train it
        except Exception as e:
            print(f"Error initializing spam detector: {e}")
            self._build_fallback_model()
    
    def init_app(self, app):
        """Initialize with app context"""
        self.app = app
        # Use the app's configured data directory if available
        if hasattr(app, 'config') and app.config.get('MODEL_DATA_DIR'):
            self.data_dir = app.config.get('MODEL_DATA_DIR')
    
    def _create_sample_data(self):
        """Create comprehensive sample training data"""
        sample_data = {
            'sms_spam.csv': {
                'text': [
                    "WINNER!! You've been selected for a free $1000 gift card. Text YES to claim!",
                    "Urgent: Your bank account needs verification. Click http://bad-link.com to secure your account.",
                    "You've won a prize! Claim your iPhone now at http://free-iphone.com",
                    "Hi, are we still meeting tomorrow at 5pm?",
                    "Thanks for your message, I'll get back to you soon.",
                    "Can you send me the report by EOD today?"
                ],
                'text_type': ['spam', 'spam', 'spam', 'ham', 'ham', 'ham']
            },
            'email_spam.csv': {
                'text': [
                    "Investment opportunity! Double your money in 24 hours. Limited time offer!",
                    "Your account has been compromised. Verify your identity at http://secure-login.com",
                    "Nigerian prince needs your help to transfer $10,000,000. You get 20% commission.",
                    "Hello, I'm following up on our meeting yesterday.",
                    "Please find attached the documents you requested.",
                    "Looking forward to our call tomorrow at 3 PM."
                ],
                'text_type': ['spam', 'spam', 'spam', 'ham', 'ham', 'ham']
            },
            'instagram_spam.csv': {
                'text': [
                    "Get 10k followers in 24 hours! Click the link in bio!",
                    "You've been tagged in a photo! View it now at http://fake-instagram.com",
                    "Congratulations! You won our giveaway! DM us to claim your prize.",
                    "Nice post! 😊",
                    "Thanks for the follow!",
                    "Check out my latest post!"
                ],
                'text_type': ['spam', 'spam', 'spam', 'ham', 'ham', 'ham']
            },
            'telegram_spam.csv': {
                'text': [
                    "Earn $1000 daily with this simple method! Join our channel now!",
                    "Your account has suspicious activity. Verify now: http://telegram-verify.com",
                    "Free crypto signals! Join our premium group for guaranteed profits!",
                    "Hey, how are you doing?",
                    "Did you see the message I sent yesterday?",
                    "Let's schedule a meeting for next week."
                ],
                'text_type': ['spam', 'spam', 'spam', 'ham', 'ham', 'ham']
            }
        }
        
        for filename, data in sample_data.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False)
                print(f"Created sample data file: {filename}")
    
    def _load_training_data(self):
        """Load training data from multiple sources"""
        datasets = {}
        print(f"[DEBUG] Looking for training data in directory: {self.data_dir}")
        for platform in ['sms', 'email', 'instagram', 'telegram']:
            filename = f'{platform}_spam.csv'
            filepath = os.path.join(self.data_dir, filename)
            print(f"[DEBUG] Checking for file: {filepath}")
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath)
                    print(f"[DEBUG] Loaded file: {filename} with {len(df)} rows")
                    if 'text_type' not in df.columns:
                        print(f"Warning: {filename} missing 'text_type' column")
                        continue

                    # Convert numeric labels to string labels if needed
                    if df['text_type'].dtype in ['int64', 'float64'] or set(df['text_type'].unique()) <= {0, 1}:
                        df['text_type'] = df['text_type'].map({0: 'ham', 1: 'spam'})

                    if len(df['text_type'].unique()) < 2:
                        print(f"Warning: {filename} has only one class: {df['text_type'].unique()}")

                        if 'spam' in df['text_type'].unique():
                            synthetic_ham = pd.DataFrame({
                                'text': ['Hello, how are you?', 'Thanks for your message', 'Meeting tomorrow at 10am'],
                                'text_type': ['ham', 'ham', 'ham']
                                })
                            df = pd.concat([df, synthetic_ham], ignore_index=True)

                        else:
                            synthetic_spam = pd.DataFrame({
                                'text': ['Win a free iPhone!', 'Your account needs verification', 'Click here to claim prize'],
                                'text_type': ['spam', 'spam', 'spam']
                                })
                            df = pd.concat([df, synthetic_spam], ignore_index=True)

                    datasets[platform] = df
                    print(f"Loaded data from {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
 
        if not datasets:
            print("No training data found, creating synthetic data")
                
            synthetic_data = {
                    'text': [
                        "WINNER!! You've been selected for a free $1000 gift card. Text YES to claim!",
                        "Urgent: Your bank account needs verification. Click http://bad-link.com to secure your account.",
                        "You've won a prize! Claim your iPhone now at http://free-iphone.com",
                        "Hi, are we still meeting tomorrow at 5pm?",
                        "Thanks for your message, I'll get back to you soon.",
                        "Can you send me the report by EOD today?"
                        ],
                        'text_type': ['spam', 'spam', 'spam', 'ham', 'ham', 'ham']
                    }
            datasets['synthetic'] = pd.DataFrame(synthetic_data)
        
        all_data = []
        for platform, df in datasets.items():
            # If there are multiple datasets and not synthetic, sample; otherwise, use all data
            if len(datasets) > 1 and platform != 'synthetic':
                df = df.sample(frac=0.25, random_state=42)
            df['platform'] = platform
            all_data.append(df)

        if not all_data:
            raise ValueError("No training data available to concatenate.")

        self.combined_df = pd.concat(all_data, ignore_index=True)
        self.combined_df['label'] = self.combined_df['text_type'].apply(
            lambda x: 1 if x == 'spam' else 0
        )

        # Extract features
        self.combined_df['cleaned_text'] = self.combined_df['text'].apply(self.clean_text)
        self.combined_df['text_length'] = self.combined_df['text'].apply(len)
        self.combined_df['word_count'] = self.combined_df['text'].apply(lambda x: len(x.split()))
        self.combined_df['has_url'] = self.combined_df['text'].apply(self._has_url)
        self.combined_df['has_phone'] = self.combined_df['text'].apply(self._has_phone)
        self.combined_df['sentiment'] = self.combined_df['text'].apply(self._get_sentiment)
        self.combined_df['grammar_errors'] = self.combined_df['text'].apply(self._count_grammar_errors)

        print(f"Loaded {len(self.combined_df)} training examples")
        print(f"Class distribution: {self.combined_df['label'].value_counts().to_dict()}")
        print("[DEBUG] Label counts:")
        print(self.combined_df['label'].value_counts())
        print("[DEBUG] Sample rows:")
        print(self.combined_df[['text', 'text_type', 'label']].head())

    def _build_model(self):
        """Build an advanced model with multiple feature types"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import OneHotEncoder, StandardScaler
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.ensemble import RandomForestClassifier

        # Text features
        text_transformer = TfidfVectorizer(
            max_features=2000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=1.0
        )
        platform_transformer = OneHotEncoder(handle_unknown='ignore')
        numeric_features = ['text_length', 'word_count', 'sentiment', 'grammar_errors']
        numeric_transformer = StandardScaler()
        bool_features = ['has_url', 'has_phone']
        bool_transformer = 'passthrough'
        preprocessor = ColumnTransformer(
            transformers=[
                ('text', text_transformer, 'cleaned_text'),
                ('platform', platform_transformer, ['platform']),
                ('numeric', numeric_transformer, numeric_features),
                ('bool', bool_transformer, bool_features)
            ]
        )
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(
                n_estimators=100,
                class_weight='balanced',
                random_state=42
            ))
        ])
        
        # Store the model in the instance
        self.model = model
        print("[DEBUG] Model built and assigned to self.model")
        return model

    def _build_fallback_model(self):
        """Build a simple fallback model"""
        self.model = Pipeline([
            ('vectorizer', TfidfVectorizer(max_features=100, stop_words='english')),
            ('classifier', RandomForestClassifier(n_estimators=10, random_state=42))
        ])
        
        # Train with basic examples
        X = [
            "win free money now", 
            "verify your account immediately",
            "click this link to claim prize",
            "hello how are you doing",
            "meeting tomorrow at 10am",
            "thanks for your email"
        ]
        y = [1, 1, 1, 0, 0, 0]
        
        self.model.fit(X, y)
        self.is_trained = True
        print("Fallback model trained with basic examples")
    
    def clean_text(self, text):
        """Clean and preprocess text"""
        if not isinstance(text, str):
            return ""
            
        text = text.lower()
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _has_url(self, text):
        """Check if text contains URLs"""
        return 1 if re.search(r'http\S+', text) else 0
    
    def _has_phone(self, text):
        """Check if text contains phone numbers"""
        return 1 if re.search(r'(\+\d{1,3}[-\.\s]??\d{1,4}[-\.\s]??\d{1,4}[-\.\s]??\d{1,4})|(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4})|(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4})', text) else 0
    
    def _get_sentiment(self, text):
        """Get text sentiment polarity"""
        try:
            return TextBlob(text).sentiment.polarity
        except:
            return 0
    
    def _count_grammar_errors(self, text):
        """Count grammar errors in text"""
        try:
            # tool = language_tool_python.LanguageTool('en-US')
            # matches = tool.check(text)
            # return len(matches)
            return 0  # Placeholder until language_tool_python is properly installed
        except:
            return 0
    
    def extract_features(self, text, platform):
        """Extract comprehensive features from text"""
        cleaned_text = self.clean_text(text)
        
        features = {
            'cleaned_text': cleaned_text,
            'platform': platform,
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_url': self._has_url(text),
            'has_phone': self._has_phone(text),
            'sentiment': self._get_sentiment(text),
            'grammar_errors': self._count_grammar_errors(text),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(1, len(text)),
            'special_char_ratio': sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(1, len(text)),
            'spam_keywords_count': self._count_spam_keywords(text)
        }
        
        return features
    
    def _count_spam_keywords(self, text):
        """Count spam-related keywords"""
        spam_keywords = [
            'win', 'free', 'prize', 'reward', 'claim', 'click', 'urgent', 'verify',
            'account', 'security', 'limited', 'offer', 'discount', 'winner', 'selected',
            'congratulations', 'lottery', 'gift', 'card', 'voucher', 'http', 'www',
            'password', 'login', 'confirm', 'update', 'information', 'personal',
            'bank', 'payment', 'money', 'cash', 'transfer', 'inheritance', 'million',
            'billion', 'dollar', 'euro', 'pound', 'bitcoin', 'crypto', 'investment',
            'opportunity', 'risk-free', 'guaranteed', 'act now', 'limited time',
            'expire', 'trial', 'subscription', 'membership', 'exclusive', 'secret',
            'miracle', 'cure', 'weight loss', 'diet', 'pills', 'viagra', 'casino',
            'betting', 'gambling', 'loan', 'credit', 'debt', 'mortgage', 'insurance'
        ]
        
        text_lower = text.lower()
        return sum(1 for keyword in spam_keywords if keyword in text_lower)
    
    def train(self, save_model=True):
        """Train the model with comprehensive evaluation"""
        try:
            if not hasattr(self, 'combined_df') or self.combined_df is None:
                print("No training data available")
                return 0, 0, 0, 0
                
            X = self.combined_df[['cleaned_text', 'platform', 'text_length', 'word_count', 
                                  'has_url', 'has_phone', 'sentiment', 'grammar_errors']]
            y = self.combined_df['label']
            
            # Check if we have both classes
            if len(y.unique()) < 2:
                print("Warning: Only one class found in training data. Adding synthetic examples.")
                # Add synthetic examples for the missing class
                if 1 not in y.unique():
                    synthetic_spam = pd.DataFrame({
                        'cleaned_text': ['win free money now', 'click here to claim prize', 'verify your account'],
                        'platform': ['synthetic'] * 3,
                        'text_length': [15, 20, 18],
                        'word_count': [3, 4, 3],
                        'has_url': [1, 1, 0],
                        'has_phone': [0, 0, 0],
                        'sentiment': [0.5, 0.6, 0.4],
                        'grammar_errors': [2, 3, 1]
                        })
                    X = pd.concat([X, synthetic_spam], ignore_index=True)
                    y = pd.concat([y, pd.Series([1, 1, 1])], ignore_index=True)
                    
                else:
                    synthetic_ham = pd.DataFrame({
                        'cleaned_text': ['hello how are you', 'meeting tomorrow at 10am', 'thanks for your message'],
                        'platform': ['synthetic'] * 3,
                        'text_length': [15, 20, 18],
                        'word_count': [3, 4, 3],
                        'has_url': [0, 0, 0],
                        'has_phone': [0, 0, 0],
                        'sentiment': [0.2, 0.1, 0.3],
                        'grammar_errors': [0, 1, 0]
                        })
                    X = pd.concat([X, synthetic_ham], ignore_index=True)
                    y = pd.concat([y, pd.Series([0, 0, 0])], ignore_index=True)
        
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
                )
            
            # Make sure we have a model to train
            if self.model is None:
                self._build_model()
                
            self.model.fit(X_train, y_train)
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            print(f"Model trained successfully. Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            self.is_trained = True
        
            if save_model:
                model_path = os.path.join(self.data_dir, 'spam_detector_model.joblib')
                joblib.dump(self.model, model_path)
                print("Model saved successfully")
        
            return accuracy, precision, recall, f1
        
        except Exception as e:
            print(f"Error training model: {e}")
            import traceback
            traceback.print_exc()
            self._build_fallback_model()
            return 0, 0, 0, 0
    
    def predict(self, text, platform='email'):
        """Make prediction with comprehensive analysis"""
        try:
            if not self.is_trained or self.model is None:
                print("Model not trained, using fallback")
                return self.fallback_predict_with_explanation(text, platform)
            
            features = self.extract_features(text, platform)
            input_data = pd.DataFrame([features])
            
            prediction = self.model.predict(input_data)[0]
            probability = self.model.predict_proba(input_data)[0][1]
            
            result = ('spam' if prediction == 1 else 'ham', round(float(probability), 3))
            explanation = self.generate_detailed_explanation(text, platform, result[0] == 'spam', features)
        
            return result[0], result[1], explanation
        
        except Exception as e:
            print(f"Error making prediction: {e}")
            import traceback
            traceback.print_exc()
            return self.fallback_predict_with_explanation(text, platform)
    
    def fallback_predict_with_explanation(self, text, platform):
        """Fallback prediction with explanation"""
        prediction, probability = self.fallback_predict(text)
        explanation = self.generate_detailed_explanation(text, platform, prediction == 'spam', {})
        return prediction, probability, explanation
    
    def fallback_predict(self, text):
        """Simple keyword-based fallback prediction"""
        spam_keywords = ['win', 'free', 'click', 'prize', 'verify', 'account', 'urgent', 'buy now', 'click here']
        text_lower = text.lower()
        
        # Count spam keywords
        spam_score = sum(1 for keyword in spam_keywords if keyword in text_lower)
        
        # If at least two spam keywords, classify as spam
        if spam_score >= 2:
            return 'spam', 0.9
        return 'ham', 0.8
    
    def generate_detailed_explanation(self, text, platform, is_spam, features):
        """Generate comprehensive explanation for the prediction"""
        explanation_parts = []
        
        if is_spam:
            explanation_parts.append("🚨 This message was classified as SPAM because it contains multiple characteristics commonly found in spam messages.")
            
            # Check for specific spam indicators
            indicators = []
            
            if features.get('has_url', 0):
                indicators.append("Contains suspicious links")
            
            if features.get('has_phone', 0):
                indicators.append("Contains phone numbers (common in scams)")
            
            spam_keyword_count = features.get('spam_keywords_count', self._count_spam_keywords(text))
            if spam_keyword_count > 0:
                indicators.append(f"Contains {spam_keyword_count} spam-related keywords")
            
            uppercase_ratio = features.get('uppercase_ratio', sum(1 for c in text if c.isupper()) / max(1, len(text)))
            if uppercase_ratio > 0.3:
                indicators.append("Uses excessive uppercase letters (common in spam)")
            
            sentiment = features.get('sentiment', self._get_sentiment(text))
            if sentiment > 0.5:
                indicators.append("Uses overly positive language (common in prize scams)")
            
            grammar_errors = features.get('grammar_errors', self._count_grammar_errors(text))
            if grammar_errors > 5:
                indicators.append("Contains multiple grammatical errors (common in spam)")
            
            if indicators:
                explanation_parts.append("\n🔍 Specific indicators detected:")
                for indicator in indicators:
                    explanation_parts.append(f"• {indicator}")
            
            explanation_parts.append("\n⚠️ Be cautious: This message may be attempting to trick you into revealing personal information or making unwanted payments.")
            
        else:
            explanation_parts.append("✅ This message appears to be legitimate (HAM) and doesn't contain obvious spam characteristics.")
            
            # Check for legitimacy indicators
            indicators = []
            
            if features.get('sentiment', self._get_sentiment(text)) >= -0.3:
                indicators.append("Uses neutral or positive language")
            
            grammar_errors = features.get('grammar_errors', self._count_grammar_errors(text))
            if grammar_errors <= 2:
                indicators.append("Contains few grammatical errors")
            
            if not features.get('has_url', 0):
                indicators.append("No suspicious links detected")
            
            if indicators:
                explanation_parts.append("\n🔍 Legitimacy indicators:")
                for indicator in indicators:
                    explanation_parts.append(f"• {indicator}")
            
            explanation_parts.append("\n💡 Tip: Always verify the identity of the sender before sharing sensitive information.")
        
        # Add platform-specific advice
        platform_advice = {
            'email': "Be especially cautious with email attachments and links, even from known senders.",
            'sms': "Never reply to suspicious text messages or call numbers provided in them.",
            'instagram': "Watch out for fake profiles and don't engage with suspicious direct messages.",
            'telegram': "Be wary of unsolicited messages in groups or from unknown contacts."
        }
        
        explanation_parts.append(f"\n📱 Platform-specific advice for {platform}:")
        explanation_parts.append(platform_advice.get(platform, "Always verify the authenticity of messages on this platform."))
        
        return "\n".join(explanation_parts)

# Global instance
spam_detector = EnhancedSpamDetector()