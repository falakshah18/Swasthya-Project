from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import json


class User(AbstractUser):
    """Extended user model for patients and ASHA workers"""
    USER_TYPES = [
        ('patient', 'Patient'),
        ('asha', 'ASHA Worker'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patient')
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')]
    )
    village = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Symptom(models.Model):
    """Symptoms model with severity levels"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    severity_score = models.IntegerField(default=1)  # 1-10 scale
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Condition(models.Model):
    """Medical conditions/diseases"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('self_care', 'Self Care'),
            ('clinic', 'Visit Clinic'),
            ('emergency', 'Emergency'),
        ]
    )
    precautions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ConditionSymptom(models.Model):
    """Many-to-many relationship between conditions and symptoms"""
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    frequency = models.IntegerField(default=1)  # How often this symptom appears with this condition

    class Meta:
        unique_together = ['condition', 'symptom']


class Facility(models.Model):
    """Healthcare facilities"""
    FACILITY_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('pharmacy', 'Pharmacy'),
    ]
    
    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_24_7 = models.BooleanField(default=False)
    opening_hours = models.JSONField(default=dict)  # Store opening hours as JSON
    services = models.JSONField(default=list)  # List of services offered
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.facility_type})"


class Patient(models.Model):
    """Patient profiles"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    medical_history = models.JSONField(default=list)
    allergies = models.JSONField(default=list)
    custom_medicines = models.JSONField(default=list)
    emergency_contact = models.CharField(max_length=15, blank=True)
    emergency_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} (Patient)"


class ChatSession(models.Model):
    """Chat sessions for symptom analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    symptoms = models.JSONField(default=list)
    predicted_conditions = models.JSONField(default=list)
    urgency_level = models.CharField(max_length=20, blank=True)
    recommended_facility_type = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id} - {self.user.get_full_name()}"


class Medicine(models.Model):
    """Medicine database"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    dosage_instructions = models.TextField(blank=True)
    side_effects = models.JSONField(default=list)
    contraindications = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MedicineReminder(models.Model):
    """Medicine reminders for patients"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medicine_reminders')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g., "twice daily", "once weekly"
    next_dose = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.medicine.name}"


class MedicineIntake(models.Model):
    """Track medicine intake"""
    reminder = models.ForeignKey(MedicineReminder, on_delete=models.CASCADE, related_name='intakes')
    taken_at = models.DateTimeField(auto_now_add=True)
    was_taken = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        status = "Taken" if self.was_taken else "Missed"
        return f"{self.reminder.medicine.name} - {status}"


class EmergencyGuide(models.Model):
    """Emergency first aid guides"""
    title = models.CharField(max_length=200)
    condition = models.CharField(max_length=100)
    steps = models.JSONField(default=list)  # List of steps
    urgency_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ]
    )
    call_emergency = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
