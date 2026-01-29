from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
from apps.rooms.models import Room, RoomType, RoomStatusLog, RoomImage, RoomAmenity, RoomTypeAmenity
from apps.reservations.models import Reservation
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
            qs = qs.filter(property=self.request.user.assigned_property)
        
        return qs
        
        floor = self.request.query_params.get('floor')
        if floor:
            qs = qs.filter(floor_id=floor)
        
        return qs.order_by('room_number')


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()


class RoomCreateView(generics.CreateAPIView):
    """Create a new room."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    
    def perform_create(self, serializer):
        # Auto-assign property if user has one
        if self.request.user.assigned_property and 'hotel' not in serializer.validated_data:
            serializer.save(hotel=self.request.user.assigned_property)
        else:
            serializer.save()


class UpdateRoomStatusView(APIView):
    permission_classes = [IsAuthenticated, IsHousekeepingStaff]
    
    def post(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
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
            qs = qs.filter(property=self.request.user.assigned_property)
        return qs
    
    def perform_create(self, serializer):
        """Auto-assign property if user has one."""
        if self.request.user.assigned_property and 'property' not in serializer.validated_data:
            serializer.save(property=self.request.user.assigned_property)
        else:
            serializer.save()


class RoomTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room type."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeSerializer
    
    def get_queryset(self):
        qs = RoomType.objects.prefetch_related('amenities__amenity')
        if self.request.user.assigned_property:
            qs = qs.filter(property=self.request.user.assigned_property)
        return qs


class AvailabilityView(APIView):
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        check_in = request.query_params.get('check_in', date.today().isoformat())
        check_out = request.query_params.get('check_out', (date.today() + timedelta(days=1)).isoformat())
        
        check_in = date.fromisoformat(check_in)
        check_out = date.fromisoformat(check_out)
        
        # Get all room types
        room_types = RoomType.objects.filter(is_active=True)
        if request.user.assigned_property:
            room_types = room_types.filter(property=request.user.assigned_property)
        
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
        
        return Response({
            'check_in': check_in,
            'check_out': check_out,
            'availability': availability
        })


class RoomImageListView(generics.ListCreateAPIView):
    """List and upload room images."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomImageSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return RoomImage.objects.filter(room_id=room_id)
    
    def perform_create(self, serializer):
        room_id = self.kwargs.get('room_id')
        room = get_object_or_404(Room, pk=room_id)
        serializer.save(room=room, uploaded_by=self.request.user)


class RoomImageDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a specific room image."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomImageSerializer
    queryset = RoomImage.objects.all()
    lookup_url_kwarg = 'image_id'


class AvailableRoomsView(generics.ListAPIView):
    """Get available rooms for booking."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        check_in = self.request.query_params.get('check_in')
        check_out = self.request.query_params.get('check_out')
        
        qs = Room.objects.filter(is_active=True, status__in=['CLEAN', 'INSPECTED'])
        
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
    queryset = RoomTypeAmenity.objects.all()
    lookup_url_kwarg = 'amenity_assignment_id'
