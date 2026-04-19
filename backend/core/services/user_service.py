from typing import List, Dict, Any, Optional
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db.models import Q
from ..models import User, Patient, ChatSession


class UserService:
    """Service for managing users and patients"""
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        user_type: str = 'patient',
        phone: str = "",
        village: str = "",
        first_name: str = "",
        last_name: str = "",
    ) -> User:
        """Create a new user"""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            phone=phone,
            village=village,
            first_name=first_name,
            last_name=last_name,
        )
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        user = authenticate(username=username, password=password)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    def get_users_by_type(self, user_type: str) -> List[User]:
        """Get users by type"""
        return User.objects.filter(user_type=user_type)
    
    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        try:
            user = User.objects.get(id=user_id)
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.save()
            return True
        except User.DoesNotExist:
            return False
    
    def create_patient_profile(
        self, 
        user: User, 
        age: int, 
        gender: str,
        medical_history: List[str] = None,
        allergies: List[str] = None,
        emergency_contact: str = ""
    ) -> Patient:
        """Create patient profile for a user"""
        patient = Patient.objects.create(
            user=user,
            age=age,
            gender=gender,
            medical_history=medical_history or [],
            allergies=allergies or [],
            emergency_contact=emergency_contact
        )
        return patient
    
    def get_patient_profile(self, user: User) -> Optional[Patient]:
        """Get patient profile for a user"""
        try:
            return Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            return None
    
    def update_patient_profile(
        self, 
        user: User, 
        update_data: Dict[str, Any]
    ) -> bool:
        """Update patient profile"""
        try:
            patient = Patient.objects.get(user=user)
            for key, value in update_data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            patient.save()
            return True
        except Patient.DoesNotExist:
            return False
    
    def get_patients_by_village(self, village: str) -> List[Patient]:
        """Get patients by village"""
        return Patient.objects.filter(user__village__icontains=village)
    
    def get_asha_worker_patients(self, asha_user: User) -> List[Patient]:
        """Get patients assigned to an ASHA worker"""
        # This would typically involve a relationship model
        # For now, get patients from the same village
        if asha_user.village:
            return self.get_patients_by_village(asha_user.village)
        return []
    
    def verify_user(self, user_id: int) -> bool:
        """Verify a user account"""
        try:
            user = User.objects.get(id=user_id)
            user.is_verified = True
            user.save()
            return True
        except User.DoesNotExist:
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account"""
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return True
        except User.DoesNotExist:
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics"""
        return {
            'total_users': User.objects.count(),
            'patients': User.objects.filter(user_type='patient').count(),
            'asha_workers': User.objects.filter(user_type='asha').count(),
            'admins': User.objects.filter(user_type='admin').count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'active_users': User.objects.filter(is_active=True).count()
        }
    
    def search_users(self, query: str) -> List[User]:
        """Search users by name, email, or phone"""
        return User.objects.filter(
            username__icontains=query
        ).filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query)
        ).distinct()
    
    def get_user_chat_history(self, user: User) -> List[ChatSession]:
        """Get user's chat session history"""
        return ChatSession.objects.filter(user=user).order_by('-created_at')
    
    def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        """Change user password"""
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return True
        return False
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password (admin function)"""
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            return True
        except User.DoesNotExist:
            return False
