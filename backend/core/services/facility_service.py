from typing import List, Dict, Any, Optional
from django.db.models import Q
from geopy.distance import geodesic
from ..models import Facility, User


class FacilityService:
    """Service for managing healthcare facilities"""
    
    def get_nearby_facilities(
        self, 
        latitude: float, 
        longitude: float, 
        facility_type: str = None,
        radius_km: float = 10.0
    ) -> List[Facility]:
        """Get nearby facilities within radius"""
        facilities = Facility.objects.all()
        
        if facility_type:
            facilities = facilities.filter(facility_type=facility_type)
        
        nearby_facilities = []
        user_location = (latitude, longitude)
        
        for facility in facilities:
            if facility.latitude and facility.longitude:
                facility_location = (facility.latitude, facility.longitude)
                distance = geodesic(user_location, facility_location).kilometers
                
                if distance <= radius_km:
                    facility.distance = distance
                    nearby_facilities.append(facility)
        
        # Sort by distance
        nearby_facilities.sort(key=lambda x: x.distance)
        return nearby_facilities
    
    def get_facilities_by_type(self, facility_type: str) -> List[Facility]:
        """Get facilities by type"""
        return Facility.objects.filter(facility_type=facility_type)
    
    def search_facilities(self, query: str) -> List[Facility]:
        """Search facilities by name or address"""
        return Facility.objects.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query) |
            Q(services__contains=[query])
        ).distinct()
    
    def get_facility_details(self, facility_id: int) -> Optional[Facility]:
        """Get detailed facility information"""
        try:
            return Facility.objects.get(id=facility_id)
        except Facility.DoesNotExist:
            return None
    
    def is_facility_open(self, facility: Facility) -> bool:
        """Check if facility is currently open"""
        if facility.is_24_7:
            return True
        
        # Simple check - in production, implement proper time-based logic
        return True
    
    def get_open_facilities(self, facility_type: str = None) -> List[Facility]:
        """Get currently open facilities"""
        facilities = Facility.objects.filter(is_24_7=True)
        
        if facility_type:
            facilities = facilities.filter(facility_type=facility_type)
        
        return facilities
    
    def recommend_facility(
        self, 
        latitude: float, 
        longitude: float, 
        urgency_level: str,
        facility_type: str = None
    ) -> Optional[Facility]:
        """Recommend best facility based on location and urgency"""
        
        # Determine facility type based on urgency
        if not facility_type:
            facility_mapping = {
                'emergency': 'hospital',
                'clinic': 'clinic',
                'self_care': 'pharmacy'
            }
            facility_type = facility_mapping.get(urgency_level, 'clinic')
        
        # Get nearby facilities of recommended type
        nearby = self.get_nearby_facilities(
            latitude, longitude, facility_type, radius_km=20.0
        )
        
        if not nearby:
            # Fallback to any facility
            nearby = self.get_nearby_facilities(
                latitude, longitude, None, radius_km=20.0
            )
        
        # Return the closest facility
        return nearby[0] if nearby else None
    
    def create_facility(self, facility_data: Dict[str, Any]) -> Facility:
        """Create a new facility"""
        return Facility.objects.create(**facility_data)
    
    def update_facility(self, facility_id: int, update_data: Dict[str, Any]) -> bool:
        """Update facility information"""
        try:
            facility = Facility.objects.get(id=facility_id)
            for key, value in update_data.items():
                setattr(facility, key, value)
            facility.save()
            return True
        except Facility.DoesNotExist:
            return False
    
    def delete_facility(self, facility_id: int) -> bool:
        """Delete a facility"""
        try:
            facility = Facility.objects.get(id=facility_id)
            facility.delete()
            return True
        except Facility.DoesNotExist:
            return False
