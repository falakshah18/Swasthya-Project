from typing import List, Dict, Any, Optional
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Medicine, MedicineReminder, MedicineIntake, Patient


class MedicineService:
    """Service for managing medicines and reminders"""
    
    def create_medicine(self, medicine_data: Dict[str, Any]) -> Medicine:
        """Create a new medicine"""
        return Medicine.objects.create(**medicine_data)
    
    def get_medicines(self, search_query: str = None) -> List[Medicine]:
        """Get medicines, optionally filtered by search query"""
        if search_query:
            return Medicine.objects.filter(name__icontains=search_query)
        return Medicine.objects.all()
    
    def get_medicine_details(self, medicine_id: int) -> Optional[Medicine]:
        """Get detailed medicine information"""
        try:
            return Medicine.objects.get(id=medicine_id)
        except Medicine.DoesNotExist:
            return None
    
    def create_reminder(
        self, 
        patient: Patient, 
        medicine: Medicine, 
        dosage: str,
        frequency: str,
        next_dose: datetime,
        notes: str = ""
    ) -> MedicineReminder:
        """Create a medicine reminder for a patient"""
        return MedicineReminder.objects.create(
            patient=patient,
            medicine=medicine,
            dosage=dosage,
            frequency=frequency,
            next_dose=next_dose,
            notes=notes
        )
    
    def get_patient_reminders(self, patient: Patient, active_only: bool = True) -> List[MedicineReminder]:
        """Get medicine reminders for a patient"""
        reminders = MedicineReminder.objects.filter(patient=patient)
        if active_only:
            reminders = reminders.filter(is_active=True)
        return reminders.order_by('next_dose')
    
    def get_upcoming_reminders(self, patient: Patient, hours_ahead: int = 24) -> List[MedicineReminder]:
        """Get upcoming reminders within specified hours"""
        cutoff_time = timezone.now() + timedelta(hours=hours_ahead)
        return MedicineReminder.objects.filter(
            patient=patient,
            is_active=True,
            next_dose__lte=cutoff_time
        ).order_by('next_dose')
    
    def get_overdue_reminders(self, patient: Patient) -> List[MedicineReminder]:
        """Get overdue reminders"""
        now = timezone.now()
        return MedicineReminder.objects.filter(
            patient=patient,
            is_active=True,
            next_dose__lt=now
        ).order_by('next_dose')
    
    def record_intake(self, reminder: MedicineReminder, was_taken: bool, notes: str = "") -> MedicineIntake:
        """Record medicine intake"""
        intake = MedicineIntake.objects.create(
            reminder=reminder,
            was_taken=was_taken,
            notes=notes
        )
        
        # Update next dose time if taken
        if was_taken:
            self._schedule_next_dose(reminder)
        
        return intake
    
    def get_intake_history(
        self, 
        patient: Patient, 
        days: int = 30
    ) -> List[MedicineIntake]:
        """Get medicine intake history for a patient"""
        cutoff_date = timezone.now() - timedelta(days=days)
        return MedicineIntake.objects.filter(
            reminder__patient=patient,
            taken_at__gte=cutoff_date
        ).order_by('-taken_at')
    
    def get_adherence_rate(self, patient: Patient, days: int = 30) -> float:
        """Calculate medicine adherence rate for a patient"""
        cutoff_date = timezone.now() - timedelta(days=days)
        intakes = MedicineIntake.objects.filter(
            reminder__patient=patient,
            taken_at__gte=cutoff_date
        )
        
        if not intakes.exists():
            return 0.0
        
        taken_count = intakes.filter(was_taken=True).count()
        return (taken_count / intakes.count()) * 100
    
    def toggle_reminder_status(self, reminder_id: int) -> bool:
        """Toggle reminder active status"""
        try:
            reminder = MedicineReminder.objects.get(id=reminder_id)
            reminder.is_active = not reminder.is_active
            reminder.save()
            return True
        except MedicineReminder.DoesNotExist:
            return False
    
    def update_reminder(self, reminder_id: int, update_data: Dict[str, Any]) -> bool:
        """Update reminder information"""
        try:
            reminder = MedicineReminder.objects.get(id=reminder_id)
            for key, value in update_data.items():
                setattr(reminder, key, value)
            reminder.save()
            return True
        except MedicineReminder.DoesNotExist:
            return False
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """Delete a reminder"""
        try:
            reminder = MedicineReminder.objects.get(id=reminder_id)
            reminder.delete()
            return True
        except MedicineReminder.DoesNotExist:
            return False
    
    def _schedule_next_dose(self, reminder: MedicineReminder):
        """Schedule the next dose based on frequency"""
        frequency_mapping = {
            'once daily': 1,
            'twice daily': 0.5,
            'three times daily': 0.33,
            'once weekly': 7,
            'once monthly': 30
        }
        
        days_to_add = frequency_mapping.get(reminder.frequency.lower(), 1)
        reminder.next_dose = timezone.now() + timedelta(days=days_to_add)
        reminder.save()
    
    def get_medicine_interactions(self, medicine_ids: List[int]) -> List[Dict[str, Any]]:
        """Check for potential medicine interactions"""
        medicines = Medicine.objects.filter(id__in=medicine_ids)
        
        # Simplified interaction checking
        interactions = []
        for i, med1 in enumerate(medicines):
            for med2 in medicines[i+1:]:
                # Check for contraindications
                if med2.name in med1.contraindications:
                    interactions.append({
                        'medicine1': med1.name,
                        'medicine2': med2.name,
                        'severity': 'high',
                        'description': f"{med1.name} should not be taken with {med2.name}"
                    })
        
        return interactions
