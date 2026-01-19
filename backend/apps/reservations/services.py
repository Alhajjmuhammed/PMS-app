"""
Room Availability Service
Handles availability checking, booking conflicts, and room allocation
"""

from datetime import datetime, timedelta
from django.db.models import Q
from apps.rooms.models import Room
from apps.reservations.models import Reservation


class AvailabilityService:
    """Service for checking room availability and managing bookings."""
    
    @staticmethod
    def check_availability(room_id, check_in_date, check_out_date, exclude_reservation_id=None):
        """
        Check if a room is available for given dates.
        
        Args:
            room_id: ID of the room to check
            check_in_date: Check-in date
            check_out_date: Check-out date
            exclude_reservation_id: Optional reservation ID to exclude (for updates)
            
        Returns:
            bool: True if available, False otherwise
        """
        from apps.reservations.models import ReservationRoom
        
        # Build query for conflicting reservation rooms
        query = Q(
            room_id=room_id,
            reservation__status__in=['CONFIRMED', 'CHECKED_IN']
        )
        
        # Check for date overlap
        date_overlap = Q(
            reservation__check_in_date__lt=check_out_date,
            reservation__check_out_date__gt=check_in_date
        )
        
        query &= date_overlap
        
        # Exclude specific reservation (for updates)
        if exclude_reservation_id:
            query &= ~Q(reservation_id=exclude_reservation_id)
        
        # Check if any conflicting reservation rooms exist
        conflicts = ReservationRoom.objects.filter(query).exists()
        
        return not conflicts
    
    @staticmethod
    def get_available_rooms(hotel_id, room_type_id, check_in_date, check_out_date, count=1):
        """
        Get list of available rooms for given criteria.
        
        Args:
            hotel_id: Hotel/Property ID
            room_type_id: Room type ID (optional)
            check_in_date: Check-in date
            check_out_date: Check-out date
            count: Number of rooms needed
            
        Returns:
            QuerySet: Available rooms
        """
        # Get all rooms matching criteria
        rooms = Room.objects.filter(
            hotel_id=hotel_id,
            is_active=True,
            status='VC'  # Vacant Clean
        )
        
        if room_type_id:
            rooms = rooms.filter(room_type_id=room_type_id)
        
        # Filter out rooms with conflicting reservations
        available_rooms = []
        for room in rooms:
            if AvailabilityService.check_availability(
                room.id, check_in_date, check_out_date
            ):
                available_rooms.append(room.id)
                if len(available_rooms) >= count:
                    break
        
        return Room.objects.filter(id__in=available_rooms)
    
    @staticmethod
    def get_availability_calendar(hotel_id, room_type_id, start_date, end_date):
        """
        Get availability calendar for a date range.
        
        Args:
            hotel_id: Hotel/Property ID
            room_type_id: Room type ID (optional)
            start_date: Start date
            end_date: End date
            
        Returns:
            dict: Availability data by date
        """
        # Get all rooms
        rooms = Room.objects.filter(
            hotel_id=hotel_id,
            is_active=True
        )
        
        if room_type_id:
            rooms = rooms.filter(room_type_id=room_type_id)
        
        total_rooms = rooms.count()
        
        # Get all reservation rooms in date range
        from apps.reservations.models import ReservationRoom
        
        reservation_rooms = ReservationRoom.objects.filter(
            room__in=rooms,
            reservation__status__in=['CONFIRMED', 'CHECKED_IN'],
            reservation__check_in_date__lt=end_date,
            reservation__check_out_date__gt=start_date
        ).select_related('room', 'reservation')
        
        # Build calendar
        calendar = {}
        current_date = start_date
        
        while current_date < end_date:
            next_date = current_date + timedelta(days=1)
            
            # Count occupied rooms for this date
            occupied = reservation_rooms.filter(
                reservation__check_in_date__lt=next_date,
                reservation__check_out_date__gt=current_date
            ).values('room').distinct().count()
            
            available = total_rooms - occupied
            occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
            
            calendar[current_date.isoformat()] = {
                'date': current_date.isoformat(),
                'total_rooms': total_rooms,
                'occupied': occupied,
                'available': available,
                'occupancy_rate': round(occupancy_rate, 2)
            }
            
            current_date = next_date
        
        return calendar
    
    @staticmethod
    def validate_booking_dates(check_in_date, check_out_date):
        """
        Validate booking dates.
        
        Args:
            check_in_date: Check-in date
            check_out_date: Check-out date
            
        Returns:
            tuple: (is_valid, error_message)
        """
        today = datetime.now().date()
        
        # Check-in must be in the future (or today for same-day bookings)
        if check_in_date < today:
            return False, "Check-in date cannot be in the past"
        
        # Check-out must be after check-in
        if check_out_date <= check_in_date:
            return False, "Check-out date must be after check-in date"
        
        # Maximum stay validation (optional, configure as needed)
        max_stay_days = 365
        nights = (check_out_date - check_in_date).days
        if nights > max_stay_days:
            return False, f"Maximum stay is {max_stay_days} nights"
        
        return True, None
    
    @staticmethod
    def get_overlapping_reservations(room_id, check_in_date, check_out_date):
        """
        Get all reservations that overlap with given dates.
        
        Args:
            room_id: Room ID
            check_in_date: Check-in date
            check_out_date: Check-out date
            
        Returns:
            QuerySet: Overlapping reservations
        """
        from apps.reservations.models import ReservationRoom
        
        reservation_rooms = ReservationRoom.objects.filter(
            room_id=room_id,
            reservation__status__in=['CONFIRMED', 'CHECKED_IN'],
            reservation__check_in_date__lt=check_out_date,
            reservation__check_out_date__gt=check_in_date
        ).select_related('reservation__guest', 'room')
        
        return Reservation.objects.filter(
            id__in=reservation_rooms.values_list('reservation_id', flat=True)
        ).select_related('guest')
    
    @staticmethod
    def suggest_alternative_rooms(hotel_id, room_type_id, check_in_date, check_out_date):
        """
        Suggest alternative rooms if requested room is not available.
        
        Args:
            hotel_id: Hotel/Property ID
            room_type_id: Requested room type ID
            check_in_date: Check-in date
            check_out_date: Check-out date
            
        Returns:
            dict: Suggested rooms by room type
        """
        from apps.rooms.models import RoomType
        
        suggestions = {}
        
        # Get all room types for the property
        room_types = RoomType.objects.filter(
            hotel_id=hotel_id,
            is_active=True
        ).exclude(id=room_type_id)
        
        for room_type in room_types:
            available = AvailabilityService.get_available_rooms(
                hotel_id, room_type.id, check_in_date, check_out_date, count=3
            )
            
            if available.exists():
                suggestions[room_type.name] = {
                    'room_type_id': room_type.id,
                    'room_type_name': room_type.name,
                    'base_rate': str(room_type.base_rate),
                    'available_count': available.count(),
                    'rooms': list(available.values('id', 'room_number'))
                }
        
        return suggestions
