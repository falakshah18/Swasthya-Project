from rest_framework import serializers
from .models import (
    User, Symptom, Condition, ConditionSymptom, Facility, 
    Patient, ChatSession, Medicine, MedicineReminder, 
    MedicineIntake, EmergencyGuide
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'phone', 'village', 'is_verified',
            'created_at', 'updated_at', 'full_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class SymptomSerializer(serializers.ModelSerializer):
    """Serializer for Symptom model"""
    
    class Meta:
        model = Symptom
        fields = '__all__'


class ConditionSerializer(serializers.ModelSerializer):
    """Serializer for Condition model"""
    
    class Meta:
        model = Condition
        fields = '__all__'


class ConditionSymptomSerializer(serializers.ModelSerializer):
    """Serializer for ConditionSymptom model"""
    symptom_name = serializers.CharField(source='symptom.name', read_only=True)
    condition_name = serializers.CharField(source='condition.name', read_only=True)
    
    class Meta:
        model = ConditionSymptom
        fields = '__all__'


class FacilitySerializer(serializers.ModelSerializer):
    """Serializer for Facility model"""
    distance = serializers.SerializerMethodField()
    is_open_now = serializers.SerializerMethodField()
    
    class Meta:
        model = Facility
        fields = '__all__'
    
    def get_distance(self, obj):
        return getattr(obj, 'distance', None)
    
    def get_is_open_now(self, obj):
        # Simple check - implement proper time-based logic
        return obj.is_24_7


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model"""
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession model"""
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = '__all__'


class MedicineSerializer(serializers.ModelSerializer):
    """Serializer for Medicine model"""
    
    class Meta:
        model = Medicine
        fields = '__all__'


class MedicineReminderSerializer(serializers.ModelSerializer):
    """Serializer for MedicineReminder model"""
    patient_info = PatientSerializer(source='patient', read_only=True)
    medicine_info = MedicineSerializer(source='medicine', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicineReminder
        fields = '__all__'
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        return obj.next_dose < timezone.now() and obj.is_active


class MedicineIntakeSerializer(serializers.ModelSerializer):
    """Serializer for MedicineIntake model"""
    medicine_name = serializers.CharField(source='reminder.medicine.name', read_only=True)
    
    class Meta:
        model = MedicineIntake
        fields = '__all__'


class EmergencyGuideSerializer(serializers.ModelSerializer):
    """Serializer for EmergencyGuide model"""
    
    class Meta:
        model = EmergencyGuide
        fields = '__all__'


# Request/Response Serializers for API endpoints

class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat requests"""
    message = serializers.CharField(max_length=1000)
    session_id = serializers.CharField(required=False)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    status = serializers.CharField()
    message = serializers.CharField()
    symptoms = serializers.ListField(child=serializers.CharField(), required=False)
    predicted_conditions = serializers.ListField(child=serializers.CharField(), required=False)
    urgency_level = serializers.CharField(required=False)
    recommended_facility = serializers.CharField(required=False)
    precautions = serializers.ListField(child=serializers.CharField(), required=False)
    session_id = serializers.CharField(required=False)


class FacilitySearchRequestSerializer(serializers.Serializer):
    """Serializer for facility search requests"""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    facility_type = serializers.CharField(required=False)
    radius_km = serializers.FloatField(default=10.0)


class PatientRegistrationSerializer(serializers.Serializer):
    """Serializer for patient registration"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=15)
    village = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=Patient.GENDER_CHOICES)
    medical_history = serializers.ListField(child=serializers.CharField(), required=False)
    allergies = serializers.ListField(child=serializers.CharField(), required=False)
    emergency_contact = serializers.CharField(max_length=15, required=False)


class MedicineReminderRequestSerializer(serializers.Serializer):
    """Serializer for medicine reminder requests"""
    medicine_id = serializers.IntegerField()
    dosage = serializers.CharField(max_length=100)
    frequency = serializers.CharField(max_length=100)
    next_dose = serializers.DateTimeField()
    notes = serializers.CharField(required=False)


class LoginRequestSerializer(serializers.Serializer):
    """Serializer for login requests"""
    username = serializers.CharField()
    password = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login responses"""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserSerializer()
    patient_info = PatientSerializer(required=False)
