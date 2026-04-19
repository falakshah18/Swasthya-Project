import os
import sys
import django
import pandas as pd
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swasthya_django.settings')
django.setup()

from core.models import Symptom, Condition, ConditionSymptom, Facility, EmergencyGuide, Medicine


def load_symptoms_from_csv():
    """Load symptoms from the training data"""
    print("Loading symptoms...")
    
    try:
        # Load training data to extract symptoms
        train_df = pd.read_csv(BASE_DIR / 'core' / 'data' / 'Training.csv')
        severity_df = pd.read_csv(BASE_DIR / 'core' / 'data' / 'Symptom_severity.csv', names=['Symptom', 'Severity'])
        
        # Get symptom columns (all columns except 'prognosis')
        symptom_columns = [col for col in train_df.columns if col != 'prognosis']
        
        # Create symptom objects
        symptoms_created = 0
        for symptom_name in symptom_columns:
            # Get severity from severity dataframe
            severity_row = severity_df[severity_df['Symptom'] == symptom_name]
            severity_score = 1  # Default severity
            if not severity_row.empty:
                severity_score = int(severity_row['Severity'].iloc[0])
            
            # Determine category based on symptom name
            category = categorize_symptom(symptom_name)
            
            symptom, created = Symptom.objects.get_or_create(
                name=symptom_name,
                defaults={
                    'description': f"Symptom: {symptom_name}",
                    'severity_score': severity_score,
                    'category': category
                }
            )
            
            if created:
                symptoms_created += 1
        
        print(f"Created {symptoms_created} new symptoms")
        return True
        
    except Exception as e:
        print(f"Error loading symptoms: {e}")
        return False


def categorize_symptom(symptom_name):
    """Categorize symptom based on keywords"""
    symptom_lower = symptom_name.lower()
    
    categories = {
        'respiratory': ['cough', 'breath', 'throat', 'congestion', 'phlegm'],
        'digestive': ['stomach', 'abdominal', 'vomit', 'diarrhea', 'nausea', 'appetite'],
        'neurological': ['headache', 'dizziness', 'confusion', 'memory', 'seizure'],
        'cardiovascular': ['chest', 'heart', 'blood', 'pressure'],
        'fever': ['fever', 'temperature', 'chills', 'sweating'],
        'pain': ['pain', 'ache', 'discomfort'],
        'skin': ['skin', 'rash', 'itch', 'swelling'],
        'general': ['fatigue', 'weakness', 'weight', 'sleep']
    }
    
    for category, keywords in categories.items():
        if any(keyword in symptom_lower for keyword in keywords):
            return category
    
    return 'other'


def load_conditions_from_csv():
    """Load conditions from training data"""
    print("Loading conditions...")
    
    try:
        train_df = pd.read_csv(BASE_DIR / 'core' / 'data' / 'Training.csv')
        desc_df = pd.read_csv(BASE_DIR / 'core' / 'data' / 'symptom_Description.csv', names=['Disease', 'Description'])
        precaution_df = pd.read_csv(BASE_DIR / 'core' / 'data' / 'symptom_precaution.csv', names=['Disease', 'Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4'])
        
        # Get unique conditions
        conditions = train_df['prognosis'].unique()
        
        conditions_created = 0
        for condition_name in conditions:
            # Get description
            desc_row = desc_df[desc_df['Disease'] == condition_name]
            description = f"Medical condition: {condition_name}"
            if not desc_row.empty:
                description = desc_row['Description'].iloc[0]
            
            # Get precautions
            precautions = []
            precaution_row = precaution_df[precaution_df['Disease'] == condition_name]
            if not precaution_row.empty:
                for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                    precaution = precaution_row[col].iloc[0]
                    if pd.notna(precaution):
                        precautions.append(precaution)
            
            # Determine urgency level (simplified logic)
            urgency_level = determine_urgency_level(condition_name)
            
            condition, created = Condition.objects.get_or_create(
                name=condition_name,
                defaults={
                    'description': description,
                    'urgency_level': urgency_level,
                    'precautions': precautions
                }
            )
            
            if created:
                conditions_created += 1
        
        print(f"Created {conditions_created} new conditions")
        return True
        
    except Exception as e:
        print(f"Error loading conditions: {e}")
        return False


def determine_urgency_level(condition_name):
    """Determine urgency level based on condition name"""
    condition_lower = condition_name.lower()
    
    emergency_keywords = ['heart', 'emergency', 'severe', 'acute', 'critical']
    clinic_keywords = ['infection', 'disease', 'disorder', 'syndrome']
    
    if any(keyword in condition_lower for keyword in emergency_keywords):
        return 'emergency'
    elif any(keyword in condition_lower for keyword in clinic_keywords):
        return 'clinic'
    else:
        return 'self_care'


def load_condition_symptoms():
    """Create condition-symptom relationships"""
    print("Loading condition-symptom relationships...")
    
    try:
        train_df = pd.read_csv(BASE_DIR / 'core' / 'data' / 'Training.csv')
        
        relationships_created = 0
        for _, row in train_df.iterrows():
            condition_name = row['prognosis']
            condition = Condition.objects.filter(name=condition_name).first()
            
            if condition:
                # Get symptoms for this condition
                for symptom_name, value in row.items():
                    if symptom_name != 'prognosis' and value == 1:
                        symptom = Symptom.objects.filter(name=symptom_name).first()
                        if symptom:
                            relation, created = ConditionSymptom.objects.get_or_create(
                                condition=condition,
                                symptom=symptom,
                                defaults={'frequency': 1}
                            )
                            if created:
                                relationships_created += 1
        
        print(f"Created {relationships_created} condition-symptom relationships")
        return True
        
    except Exception as e:
        print(f"Error loading condition-symptom relationships: {e}")
        return False


def load_facilities():
    """Load facilities from JSON file"""
    print("Loading facilities...")
    
    try:
        import json
        with open(BASE_DIR / 'core' / 'data' / 'facilities.json', 'r') as f:
            facilities_data = json.load(f)
        
        facilities_created = 0
        for facility_data in facilities_data:
            facility, created = Facility.objects.get_or_create(
                name=facility_data['name'],
                defaults={
                    'facility_type': facility_data.get('type', 'hospital'),
                    'address': facility_data.get('address', ''),
                    'phone': facility_data.get('phone', ''),
                    'latitude': facility_data.get('lat'),
                    'longitude': facility_data.get('lng'),
                    'is_24_7': facility_data.get('is_24_7', False),
                    'opening_hours': facility_data.get('opening_hours', {}),
                    'services': facility_data.get('services', [])
                }
            )
            
            if created:
                facilities_created += 1
        
        print(f"Created {facilities_created} new facilities")
        return True
        
    except Exception as e:
        print(f"Error loading facilities: {e}")
        return False


def create_emergency_guides():
    """Create basic emergency guides"""
    print("Creating emergency guides...")
    
    emergency_data = [
        {
            'title': 'Heart Attack',
            'condition': 'Heart Attack',
            'steps': [
                'Call emergency services immediately (108)',
                'Keep the person calm and still',
                'Loosen tight clothing',
                'Give aspirin if available and not allergic',
                'Monitor breathing and pulse'
            ],
            'urgency_level': 'high',
            'call_emergency': True
        },
        {
            'title': 'Choking',
            'condition': 'Choking',
            'steps': [
                'Ask person to cough forcefully',
                'Perform 5 back blows',
                'Perform 5 abdominal thrusts (Heimlich)',
                'Repeat until object is expelled',
                'Call emergency services if unsuccessful'
            ],
            'urgency_level': 'high',
            'call_emergency': True
        },
        {
            'title': 'Bleeding',
            'condition': 'Bleeding',
            'steps': [
                'Apply direct pressure with clean cloth',
                'Elevate the injured area if possible',
                'Apply pressure bandage',
                'Seek medical attention for severe bleeding',
                'Keep person warm and calm'
            ],
            'urgency_level': 'medium',
            'call_emergency': False
        },
        {
            'title': 'Fever',
            'condition': 'Fever',
            'steps': [
                'Rest and stay hydrated',
                'Take lukewarm bath',
                'Use light clothing',
                'Take fever-reducing medication',
                'Seek medical help if fever persists'
            ],
            'urgency_level': 'low',
            'call_emergency': False
        }
    ]
    
    guides_created = 0
    for guide_data in emergency_data:
        guide, created = EmergencyGuide.objects.get_or_create(
            title=guide_data['title'],
            defaults=guide_data
        )
        if created:
            guides_created += 1
    
    print(f"Created {guides_created} emergency guides")
    return True


def create_basic_medicines():
    """Create basic medicine entries"""
    print("Creating basic medicines...")
    
    medicines_data = [
        {
            'name': 'Paracetamol',
            'description': 'Common pain reliever and fever reducer',
            'dosage_instructions': '500mg every 4-6 hours as needed',
            'side_effects': ['Nausea', 'Stomach upset'],
            'contraindications': ['Liver disease', 'Alcohol abuse']
        },
        {
            'name': 'Ibuprofen',
            'description': 'Anti-inflammatory pain medication',
            'dosage_instructions': '200-400mg every 6-8 hours with food',
            'side_effects': ['Stomach irritation', 'Dizziness'],
            'contraindications': ['Stomach ulcers', 'Kidney disease']
        },
        {
            'name': 'Aspirin',
            'description': 'Blood thinner and pain reliever',
            'dosage_instructions': '75-325mg daily as prescribed',
            'side_effects': ['Stomach bleeding', 'Ringing in ears'],
            'contraindications': ['Bleeding disorders', 'Pregnancy']
        }
    ]
    
    medicines_created = 0
    for medicine_data in medicines_data:
        medicine, created = Medicine.objects.get_or_create(
            name=medicine_data['name'],
            defaults=medicine_data
        )
        if created:
            medicines_created += 1
    
    print(f"Created {medicines_created} medicines")
    return True


def main():
    """Main migration function"""
    print("Starting data migration...")
    
    success_count = 0
    total_operations = 6
    
    if load_symptoms_from_csv():
        success_count += 1
    
    if load_conditions_from_csv():
        success_count += 1
    
    if load_condition_symptoms():
        success_count += 1
    
    if load_facilities():
        success_count += 1
    
    if create_emergency_guides():
        success_count += 1
    
    if create_basic_medicines():
        success_count += 1
    
    print(f"\nMigration completed: {success_count}/{total_operations} operations successful")
    
    if success_count == total_operations:
        print("All data loaded successfully!")
    else:
        print("Some operations failed. Please check the error messages above.")


if __name__ == '__main__':
    main()
