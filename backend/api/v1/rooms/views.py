from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
from datetime import date, timedelta
from apps.rooms.models import Room, RoomType, RoomStatusLog, RoomImage, RoomAmenity, RoomTypeAmenity
from apps.reservations.models import Reservation
from apps.core.cache_utils import CacheManager
from api.permissions import IsHousekeepingStaff, IsAdminOrManager, IsFrontDeskOrAbove
from .serializers import (
    RoomSerializer, RoomTypeSerializer, RoomStatusUpdateSerializer, 
    RoomImageSerializer, RoomAmenitySerializer, RoomAmenityListSerializer,
    RoomTypeAmenitySerializer
)


class RoomListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'room_type', 'floor']
    search_fields = ['room_number', 'room_type__name']
    ordering_fields = ['room_number', 'floor', 'status']
    ordering = ['room_number']
    
    def get_queryset(self):
        qs = Room.objects.select_related('room_type', 'floor__building').filter(is_active=True)
        
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        
        floor = self.request.query_params.get('floor')
        if floor:
            qs = qs.filter(floor_id=floor)
        
        return qs.order_by('room_number')


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        qs = Room.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs


class RoomCreateView(generics.CreateAPIView):
    """Create a new room."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        qs = Room.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs
    
    def perform_create(self, serializer):
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(hotel=prop)
        else:
            serializer.save()


class UpdateRoomStatusView(APIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def post(self, request, pk):
        prop = request.user.assigned_property
        try:
            room_qs = Room.objects.all()
            if prop:
                room_qs = room_qs.filter(hotel=prop)
            room = room_qs.get(pk=pk)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoomStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = room.status
        room.status = serializer.validated_data['status']
        
        if 'fo_status' in serializer.validated_data:
            room.fo_status = serializer.validated_data['fo_status']
        
        if 'notes' in serializer.validated_data:
            room.notes = serializer.validated_data['notes']
        
        room.save()
        
        # Log the status change
        RoomStatusLog.objects.create(
            room=room,
            old_status=old_status,
            new_status=room.status,
            changed_by=request.user,
            notes=serializer.validated_data.get('notes', '')
        )
        
        return Response(RoomSerializer(room).data)


class RoomTypeListView(generics.ListCreateAPIView):
    """List all room types or create a new one."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'base_rate']
    ordering = ['name']
    
    def get_queryset(self):
        qs = RoomType.objects.prefetch_related('amenities__amenity').filter(is_active=True)
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs
    
    def perform_create(self, serializer):
        prop = self.request.user.assigned_property
        if prop:
            serializer.save(hotel=prop)
        else:
            serializer.save()


class RoomTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room type."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeSerializer
    
    def get_queryset(self):
        qs = RoomType.objects.prefetch_related('amenities__amenity')
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs


@method_decorator(ratelimit(key='user', rate='100/m', method='GET', block=False), name='dispatch')
class AvailabilityView(APIView):
    """
    Check room availability for a date range.
    
    Returns available rooms by room type for the specified date range.
    Results are cached for 10 minutes to improve performance.
    
    Query Parameters:
    - check_in (date): Check-in date in ISO format (default: today)
    - check_out (date): Check-out date in ISO format (default: tomorrow)
    
    Returns:
    - check_in: Check-in date
    - check_out: Check-out date 
    - availability: List of room types with availability info
      - room_type: Room type details
      - total: Total rooms of this type
      - occupied: Number of occupied rooms
      - available: Number of available rooms
    
    Example:
    ```
    GET /api/v1/rooms/availability/?check_in=2026-04-15&check_out=2026-04-20
    ```
    """
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        # Check if rate limited
        if getattr(request, 'limited', False):
            return Response(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        check_in_str = request.query_params.get('check_in')
        check_out_str = request.query_params.get('check_out')
        
        # Set defaults if not provided
        if not check_in_str:
            check_in = date.today()
        else:
            try:
                check_in = date.fromisoformat(str(check_in_str))
            except (ValueError, AttributeError) as e:
                return Response(
                    {'error': f'Invalid check_in date format. Use ISO format (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if not check_out_str:
            check_out = date.today() + timedelta(days=1)
        else:
            try:
                check_out = date.fromisoformat(str(check_out_str))
            except (ValueError, AttributeError) as e:
                return Response(
                    {'error': f'Invalid check_out date format. Use ISO format (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if check_out <= check_in:
            return Response(
                {'error': 'Check-out date must be after check-in date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        property_id = request.user.assigned_property.id if request.user.assigned_property else 'all'
        cache_key = f'availability_{property_id}_{check_in}_{check_out}'
        
        # Try to get from cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        # Get all room types
        room_types = RoomType.objects.filter(is_active=True)
        if request.user.assigned_property:
            room_types = room_types.filter(hotel=request.user.assigned_property)
        
        availability = []
        for room_type in room_types:
            total_rooms = Room.objects.filter(
                room_type=room_type,
                is_active=True,
                status__in=['VC', 'VD']
            ).count()
            
            # Count occupied rooms for the period
            occupied = Reservation.objects.filter(
                rooms__room_type=room_type,
                check_in_date__lt=check_out,
                check_out_date__gt=check_in,
                status__in=['CONFIRMED', 'CHECKED_IN']
            ).count()
            
            availability.append({
                'room_type': RoomTypeSerializer(room_type).data,
                'total': total_rooms,
                'occupied': occupied,
                'available': max(0, total_rooms - occupied)
            })
        
        result = {
            'check_in': check_in,
            'check_out': check_out,
            'availability': availability
        }
        
        # Cache result for 10 minutes
        cache.set(cache_key, result, 600)
        
        return Response(result)


class RoomImageListView(generics.ListCreateAPIView):
    """List and upload room images."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomImageSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return RoomImage.objects.filter(room_id=room_id)
    
    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        prop = self.request.user.assigned_property
        room_qs = Room.objects.filter(hotel=prop) if prop else Room.objects.all()
        room = get_object_or_404(room_qs, pk=room_id)
        serializer.save(room=room, uploaded_by=self.request.user)


class RoomImageDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a specific room image."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomImageSerializer
    lookup_url_kwarg = 'image_id'
    
    def get_queryset(self):
        qs = RoomImage.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(room__hotel=self.request.user.assigned_property)
        return qs


class AvailableRoomsView(generics.ListAPIView):
    """Get available rooms for booking."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        check_in = self.request.query_params.get('check_in')
        check_out = self.request.query_params.get('check_out')
        
        qs = Room.objects.filter(is_active=True, status__in=['CLEAN', 'INSPECTED'])
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        
        return qs


class RoomAmenityListCreateView(generics.ListCreateAPIView):
    """List all room amenities or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    queryset = RoomAmenity.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'category']
    ordering = ['category', 'name']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RoomAmenityListSerializer
        return RoomAmenitySerializer


class RoomAmenityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room amenity."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomAmenitySerializer
    queryset = RoomAmenity.objects.all()


class RoomTypeAmenityListCreateView(generics.ListCreateAPIView):
    """List or assign amenities to a room type."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeAmenitySerializer
    
    def get_queryset(self):
        room_type_id = self.kwargs.get('room_type_id')
        return RoomTypeAmenity.objects.filter(room_type_id=room_type_id).select_related('amenity')


class RoomTypeAmenityDetailView(generics.DestroyAPIView):
    """Remove an amenity from a room type."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeAmenitySerializer
    lookup_url_kwarg = 'amenity_assignment_id'
    
    def get_queryset(self):
        qs = RoomTypeAmenity.objects.all()
        if self.request.user.assigned_property:
            qs = qs.filter(room_type__hotel=self.request.user.assigned_property)
        return qs
