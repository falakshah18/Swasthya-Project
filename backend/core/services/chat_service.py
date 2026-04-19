import uuid
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.ensemble import RandomForestClassifier
from django.utils import timezone
from pathlib import Path

from ..models import (
    User, Symptom, Condition, ConditionSymptom, ChatSession, 
    Patient, Facility, EmergencyGuide
)


class ChatService:
    """Service for handling chat interactions and symptom analysis"""
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = self.base_dir / "data"
        self._load_ml_models()
    
    def _load_ml_models(self):
        """Load ML models and training data"""
        try:
            self.train_df = pd.read_csv(self.data_dir / "Training.csv")
            self.desc_df = pd.read_csv(self.data_dir / "symptom_Description.csv")
            self.precaution_df = pd.read_csv(self.data_dir / "symptom_precaution.csv")
            self.severity_df = pd.read_csv(self.data_dir / "Symptom_severity.csv")
            
            # Prepare training data
            X = self.train_df.drop(['prognosis'], axis=1)
            y = self.train_df['prognosis']
            
            # Train Random Forest model
            self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.rf_model.fit(X, y)
            
            self.symptom_columns = X.columns.tolist()
        except Exception as e:
            print(f"Error loading ML models: {e}")
            self.rf_model = None
            self.symptom_columns = []
    
    def create_chat_session(self, user: User) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession.objects.create(
            user=user,
            session_id=str(uuid.uuid4())
        )
        return session
    
    def analyze_symptoms(self, message: str, session: ChatSession) -> Dict[str, Any]:
        """Analyze symptoms and provide triage recommendations"""
        if not self.rf_model:
            return self._fallback_response(message)
        
        # Extract symptoms from message (simplified)
        extracted_symptoms = self._extract_symptoms(message)
        
        if not extracted_symptoms:
            return {
                "status": "no_symptoms",
                "message": "I could not clearly identify the symptoms. Please mention the main symptom, age group, and duration.",
                "urgency_level": "self_care",
                "recommended_facility": None
            }
        
        # Update session with extracted symptoms
        session.symptoms = extracted_symptoms
        session.save()
        
        # Predict conditions using ML model
        predictions = self._predict_conditions(extracted_symptoms)
        
        # Determine urgency level
        urgency_level = self._determine_urgency(extracted_symptoms, predictions)
        
        # Get recommended facility type
        facility_type = self._get_facility_type(urgency_level)
        
        # Update session
        session.predicted_conditions = predictions
        session.urgency_level = urgency_level
        session.recommended_facility_type = facility_type
        session.save()
        
        return {
            "status": "success",
            "symptoms": extracted_symptoms,
            "predicted_conditions": predictions[:3],  # Top 3 conditions
            "urgency_level": urgency_level,
            "recommended_facility": facility_type,
            "precautions": self._get_precautions(predictions[0] if predictions else None),
            "session_id": session.session_id
        }
    
    def _extract_symptoms(self, message: str) -> List[str]:
        """Extract symptoms from user message"""
        # This is a simplified extraction - in production, use NLP
        message_lower = message.lower()
        extracted = []
        
        # Common symptom keywords
        symptom_keywords = [
            'fever', 'cough', 'headache', 'chest pain', 'breathing difficulty',
            'vomiting', 'diarrhea', 'fatigue', 'dizziness', 'nausea',
            'sore throat', 'body pain', 'stomach pain', 'cold', 'flu'
        ]
        
        for symptom in symptom_keywords:
            if symptom in message_lower:
                extracted.append(symptom)
        
        return extracted
    
    def _predict_conditions(self, symptoms: List[str]) -> List[str]:
        """Predict conditions based on symptoms"""
        if not self.rf_model or not symptoms:
            return []
        
        # Create input vector for ML model
        input_vector = [0] * len(self.symptom_columns)
        
        for symptom in symptoms:
            if symptom in self.symptom_columns:
                idx = self.symptom_columns.index(symptom)
                input_vector[idx] = 1
        
        # Make prediction
        try:
            prediction = self.rf_model.predict([input_vector])
            probabilities = self.rf_model.predict_proba([input_vector])
            
            # Get top conditions with probabilities
            conditions_with_probs = list(zip(
                self.rf_model.classes_,
                probabilities[0]
            ))
            conditions_with_probs.sort(key=lambda x: x[1], reverse=True)
            
            return [cond[0] for cond in conditions_with_probs[:5]]
        except Exception as e:
            print(f"Prediction error: {e}")
            return []
    
    def _determine_urgency(self, symptoms: List[str], conditions: List[str]) -> str:
        """Determine urgency level based on symptoms and conditions"""
        high_urgency_symptoms = [
            'chest pain', 'breathing difficulty', 'severe bleeding',
            'loss of consciousness', 'severe headache'
        ]
        
        medium_urgency_symptoms = [
            'high fever', 'persistent vomiting', 'severe pain',
            'difficulty speaking'
        ]
        
        for symptom in symptoms:
            if symptom in high_urgency_symptoms:
                return 'emergency'
            elif symptom in medium_urgency_symptoms:
                return 'clinic'
        
        return 'self_care'
    
    def _get_facility_type(self, urgency_level: str) -> str:
        """Get recommended facility type based on urgency"""
        facility_mapping = {
            'emergency': 'hospital',
            'clinic': 'clinic',
            'self_care': 'pharmacy'
        }
        return facility_mapping.get(urgency_level, 'clinic')
    
    def _get_precautions(self, condition: str) -> List[str]:
        """Get precautions for a condition"""
        if not condition or self.precaution_df is None:
            return []
        
        try:
            condition_row = self.precaution_df[
                self.precaution_df['Disease'] == condition
            ]
            if not condition_row.empty:
                precautions = []
                for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                    if pd.notna(condition_row[col].iloc[0]):
                        precautions.append(condition_row[col].iloc[0])
                return precautions
        except Exception as e:
            print(f"Error getting precautions: {e}")
        
        return []
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Fallback response when ML models are not available"""
        return {
            "status": "fallback",
            "message": "I'm here to help. Please describe your symptoms clearly, including duration and severity.",
            "urgency_level": "self_care",
            "recommended_facility": None
        }
    
    def get_session_history(self, user: User, session_id: str = None) -> List[ChatSession]:
        """Get chat session history for a user"""
        queryset = ChatSession.objects.filter(user=user).order_by('-created_at')
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        return queryset
