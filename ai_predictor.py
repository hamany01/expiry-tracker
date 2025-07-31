import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import sqlite3

class ExpiryPredictor:
    def __init__(self, tracker):
        self.tracker = tracker
        self.model = None
        self.label_encoders = {}
        self.model_path = os.path.join('data', 'expiry_predictor.pkl')

    def encode_column(self, column_name, data):
        """Encode categorical data with LabelEncoder and store encoder"""
        if column_name not in self.label_encoders:
            self.label_encoders[column_name] = LabelEncoder()
            self.label_encoders[column_name].fit(data)
        return self.label_encoders[column_name].transform(data)

    def prepare_training_data(self):
        """Prepare data for training the prediction model"""
        df = pd.read_sql_query(
            "SELECT * FROM expiry_items WHERE status != 'deleted'",
            sqlite3.connect(self.tracker.db_path)
        )
        
        if len(df) < 10:
            return None, None

        df['expiry_date'] = pd.to_datetime(df['expiry_date'])
        df['days_until_expiry'] = (df['expiry_date'] - datetime.now()).dt.days

        features = pd.DataFrame()
        features['category_encoded'] = self.encode_column('category', df['category'])
        features['priority_encoded'] = self.encode_column('priority', df['priority'])
        features['source_encoded'] = self.encode_column('source', df['source'])
        features['days_created'] = (datetime.now() - pd.to_datetime(df['created_at'])).dt.days

        df['urgency_score'] = np.clip(100 - df['days_until_expiry'], 0, 100)

        return features, df['urgency_score']

    def train_model(self):
        """Train the prediction model"""
        X, y = self.prepare_training_data()

        if X is None or len(X) < 10:
            return False

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)

        joblib.dump({
            'model': self.model,
            'encoders': self.label_encoders
        }, self.model_path)

        return True

    def load_model(self):
        """Load the trained model and encoders from file"""
        if os.path.exists(self.model_path):
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.label_encoders = data['encoders']
            return True
        return False

    def predict_urgency(self, item_data):
        """Predict urgency score for a new item"""
        if self.model is None:
            if not self.load_model():
                return 50  # Default score if no model available

        try:
            features = pd.DataFrame([{
                'category_encoded': self.label_encoders['category'].transform([item_data['category']])[0],
                'priority_encoded': self.label_encoders['priority'].transform([item_data['priority']])[0],
                'source_encoded': self.label_encoders['source'].transform([item_data['source']])[0],
                'days_created': (datetime.now() - pd.to_datetime(item_data['created_at'])).days
            }])
        except Exception:
            return 50  # Fallback if encoding fails

        urgency_score = self.model.predict(features)[0]
        return max(0, min(100, urgency_score))

    def get_smart_recommendations(self):
        """Get AI-powered recommendations"""
        upcoming = self.tracker.get_upcoming_expirations(60)

        if upcoming.empty:
            return []

        recommendations = []

        for _, item in upcoming.iterrows():
            days_left = int(item['days_remaining'])

            if days_left <= 0:
                recommendation = {
                    'item': item['title'],
                    'action': 'فوري: قم بالتجديد فوراً',
                    'priority': 'عالي جداً',
                    'estimated_cost': 'تحقق من التكلفة الإضافية للتأخير'
                }
            elif days_left <= 7:
                recommendation = {
                    'item': item['title'],
                    'action': 'عاجل: ابدأ إجراءات التجديد',
                    'priority': 'عالي',
                    'estimated_cost': 'التكلفة المعتادة'
                }
            elif days_left <= 30:
                recommendation = {
                    'item': item['title'],
                    'action': 'مخطط: ابدأ التحضير للتجديد',
                    'priority': 'متوسط',
                    'estimated_cost': 'التكلفة المعتادة'
                }
            else:
                recommendation = {
                    'item': item['title'],
                    'action': 'مراقبة: ضع تذكيراً لاحقاً',
                    'priority': 'منخفض',
                    'estimated_cost': 'التكلفة المعتادة'
                }

            recommendations.append(recommendation)

        return recommendations
