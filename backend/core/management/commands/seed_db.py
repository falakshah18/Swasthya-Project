"""
Management command to seed the database with initial data.
Run: python manage.py seed_db
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed the database with facilities, medicines, and demo users'

    def handle(self, *args, **options):
        self._seed_facilities()
        self._seed_medicines()
        self._seed_demo_users()
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully.'))

    def _seed_facilities(self):
        from core.models import Facility
        data_file = Path(__file__).resolve().parent.parent.parent / 'data' / 'facilities.json'
        facilities = json.loads(data_file.read_text(encoding='utf-8'))
        created = 0
        for f in facilities:
            _, was_created = Facility.objects.get_or_create(
                name=f['name'],
                defaults={
                    'facility_type': f['type'],
                    'address': f['address'],
                    'phone': f['phone'],
                    'latitude': f.get('lat'),
                    'longitude': f.get('lon'),
                    'is_24_7': f.get('availability', '') == '24/7',
                    'services': [],
                    'opening_hours': {},
                }
            )
            if was_created:
                created += 1
        self.stdout.write(f'  Facilities: {created} created.')

    def _seed_medicines(self):
        from core.models import Medicine
        medicines = [
            {'name': 'Paracetamol', 'description': 'Fever and pain relief', 'dosage_instructions': '500mg every 6 hours'},
            {'name': 'ORS Sachet', 'description': 'Oral rehydration salts', 'dosage_instructions': 'Dissolve in 1L water, sip frequently'},
            {'name': 'Amoxicillin', 'description': 'Antibiotic for bacterial infections', 'dosage_instructions': '500mg three times daily'},
            {'name': 'Metformin', 'description': 'Diabetes management', 'dosage_instructions': '500mg twice daily with meals'},
            {'name': 'Amlodipine', 'description': 'Blood pressure control', 'dosage_instructions': '5mg once daily'},
            {'name': 'Iron + Folic Acid', 'description': 'Anaemia prevention', 'dosage_instructions': '1 tablet daily after meals'},
            {'name': 'Albendazole', 'description': 'Deworming', 'dosage_instructions': '400mg single dose'},
            {'name': 'Cetirizine', 'description': 'Antihistamine for allergies', 'dosage_instructions': '10mg once daily at night'},
        ]
        created = 0
        for m in medicines:
            _, was_created = Medicine.objects.get_or_create(name=m['name'], defaults=m)
            if was_created:
                created += 1
        self.stdout.write(f'  Medicines: {created} created.')

    def _seed_demo_users(self):
        from core.models import User, Patient, MedicineReminder, Medicine
        import uuid

        # Demo patients
        demo_patients = [
            {'first': 'Asha', 'last': 'Devi', 'age': 45, 'gender': 'F',
             'village': 'Village A', 'phone': '+919876543211',
             'history': ['Diabetes', 'Hypertension'], 'medicine': 'Metformin'},
            {'first': 'Ramesh', 'last': 'Patel', 'age': 62, 'gender': 'M',
             'village': 'Village B', 'phone': '+919876543212',
             'history': ['Hypertension'], 'medicine': 'Amlodipine'},
            {'first': 'Sunita', 'last': 'Kumari', 'age': 28, 'gender': 'F',
             'village': 'Village A', 'phone': '+919876543213',
             'history': ['Anaemia'], 'medicine': 'Iron + Folic Acid'},
            {'first': 'Mohan', 'last': 'Singh', 'age': 8, 'gender': 'M',
             'village': 'Village C', 'phone': '+919876543214',
             'history': ['Fever', 'Cough'], 'medicine': 'Paracetamol'},
        ]

        created = 0
        for p in demo_patients:
            uname = f"patient_{p['first'].lower()}_{p['last'].lower()}"
            if User.objects.filter(username=uname).exists():
                continue
            user = User.objects.create_user(
                username=uname,
                email=f"{uname}@swasthya.local",
                password='demo1234',
                user_type='patient',
                phone=p['phone'],
                village=p['village'],
                first_name=p['first'],
                last_name=p['last'],
            )
            patient = Patient.objects.create(
                user=user,
                age=p['age'],
                gender=p['gender'],
                medical_history=p['history'],
                allergies=[],
            )
            med = Medicine.objects.filter(name=p['medicine']).first()
            if med:
                MedicineReminder.objects.create(
                    patient=patient,
                    medicine=med,
                    dosage='As prescribed',
                    frequency='daily',
                    next_dose=timezone.now() + timedelta(hours=8),
                )
            created += 1

        self.stdout.write(f'  Demo patients: {created} created.')

        # Demo ASHA worker
        if not User.objects.filter(username='asha_demo').exists():
            User.objects.create_user(
                username='asha_demo',
                email='asha@demo.com',
                password='asha1234',
                user_type='asha',
                phone='+919876543210',
                village='Village A',
                first_name='Sunita',
                last_name='Devi',
            )
            self.stdout.write('  ASHA worker: asha_demo / asha1234')
