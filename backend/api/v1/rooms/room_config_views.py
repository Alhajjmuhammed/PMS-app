"""
Views for Room Configuration
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Count, Q

from apps.rooms.models import RoomType, RoomAmenity, RoomTypeAmenity, RoomImage, RoomStatusLog, Room
from .room_config_serializers import (
    RoomTypeSerializer,
    RoomTypeDetailSerializer,
    RoomAmenitySerializer,
    RoomTypeAmenitySerializer,
    RoomImageSerializer,
    RoomStatusLogSerializer,
    BulkAmenityAssignSerializer
)
from api.permissions import IsAdminOrManager, IsFrontDeskOrAbove


# ===== Room Types =====

class RoomTypeListCreateView(generics.ListCreateAPIView):
    """List all room types or create new room type."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'sort_order', 'max_occupancy', 'size_sqm']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        qs = RoomType.objects.annotate(rooms_count=Count('rooms'))
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs
    
    def perform_create(self, serializer):
        from apps.properties.models import Property
        from django.db import IntegrityError
        from rest_framework.exceptions import ValidationError as DRFValidationError
        prop = self.request.user.assigned_property or Property.objects.first()
        try:
            serializer.save(hotel=prop)
        except IntegrityError:
            raise DRFValidationError({'code': 'A room type with this code already exists for this property.'})


class RoomTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room type."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomTypeDetailSerializer
    
    def get_queryset(self):
        qs = RoomType.objects.prefetch_related('amenities', 'rooms')
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs


class ActiveRoomTypesView(generics.ListAPIView):
    """List only active room types."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeSerializer
    
    def get_queryset(self):
        qs = RoomType.objects.filter(is_active=True).order_by('sort_order', 'name')
        if self.request.user.assigned_property:
            qs = qs.filter(hotel=self.request.user.assigned_property)
        return qs


# ===== Room Amenities =====

class RoomAmenityListCreateView(generics.ListCreateAPIView):
    """
    List all room amenities or create new amenity.
    
    NOTE: Intentionally GLOBAL - Room amenities like WiFi, TV, Mini Bar, etc.
    are master data shared across all properties. Properties then assign these
    amenities to their room types via RoomTypeAmenity which IS property-scoped.
    """
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomAmenitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category']
    ordering = ['category', 'name']
    
    def get_queryset(self):
        # Intentionally global - master amenity catalog
        return RoomAmenity.objects.all()


class RoomAmenityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a room amenity.
    
    NOTE: Intentionally GLOBAL - Master amenity catalog.
    """
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomAmenitySerializer
    queryset = RoomAmenity.objects.all()


class ActiveRoomAmenitiesView(generics.ListAPIView):
    """
    List only active amenities.
    
    NOTE: Intentionally GLOBAL - Master amenity catalog.
    """
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomAmenitySerializer
    
    def get_queryset(self):
        return RoomAmenity.objects.filter(is_active=True).order_by('category', 'name')


# ===== Room Type Amenities (Assignments) =====

class RoomTypeAmenityListCreateView(generics.ListCreateAPIView):
    """List all room type amenity assignments or create new."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeAmenitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room_type', 'amenity', 'is_complimentary']
    
    def get_queryset(self):
        return RoomTypeAmenity.objects.filter(
            room_type__hotel=self.request.user.assigned_property
        ).select_related('room_type', 'amenity')


class RoomTypeAmenityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room type amenity."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomTypeAmenitySerializer
    
    def get_queryset(self):
        return RoomTypeAmenity.objects.filter(
            room_type__hotel=self.request.user.assigned_property
        ).select_related('room_type', 'amenity')


class RoomTypeAmenitiesByTypeView(generics.ListAPIView):
    """Get all amenities for a specific room type."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomTypeAmenitySerializer
    
    def get_queryset(self):
        room_type_id = self.kwargs.get('room_type_id')
        return RoomTypeAmenity.objects.filter(
            room_type_id=room_type_id,
            room_type__hotel=self.request.user.assigned_property
        ).select_related('room_type', 'amenity')


class BulkAmenityAssignView(APIView):
    """Assign multiple amenities to a room type."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request):
        serializer = BulkAmenityAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        room_type = data['room_type']
        amenities = data['amenities']
        is_complimentary = data.get('is_complimentary', True)
        quantity = data.get('quantity', 1)
        
        # Verify room type belongs to user's property
        if room_type.hotel != request.user.assigned_property:
            return Response(
                {'error': 'Room type not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        created_assignments = []
        for amenity in amenities:
            assignment, created = RoomTypeAmenity.objects.get_or_create(
                room_type=room_type,
                amenity=amenity,
                defaults={
                    'quantity': quantity,
                    'is_complimentary': is_complimentary
                }
            )
            if not created:
                assignment.quantity = quantity
                assignment.is_complimentary = is_complimentary
                assignment.save()
            created_assignments.append(assignment)
        
        response_serializer = RoomTypeAmenitySerializer(created_assignments, many=True)
        return Response({
            'message': f'Assigned {len(created_assignments)} amenities',
            'assignments': response_serializer.data
        }, status=status.HTTP_201_CREATED)


# ===== Room Images =====

class RoomImageListCreateView(generics.ListCreateAPIView):
    """List all room images or upload new image."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomImageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room', 'is_primary']
    ordering_fields = ['sort_order', 'uploaded_at']
    ordering = ['sort_order']
    
    def get_queryset(self):
        return RoomImage.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room')


class RoomImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room image."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomImageSerializer
    
    def get_queryset(self):
        return RoomImage.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room')


class RoomImagesByRoomView(generics.ListAPIView):
    """Get all images for a specific room."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomImageSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return RoomImage.objects.filter(
            room_id=room_id,
            room__hotel=self.request.user.assigned_property
        ).order_by('sort_order')


# ===== Room Status Logs =====

class RoomStatusLogListCreateView(generics.ListCreateAPIView):
    """List all room status logs or create new log."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomStatusLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room', 'previous_status', 'new_status', 'changed_by']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = RoomStatusLog.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'changed_by')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(changed_by=self.request.user)


class RoomStatusLogDetailView(generics.RetrieveAPIView):
    """Retrieve a room status log."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomStatusLogSerializer
    
    def get_queryset(self):
        return RoomStatusLog.objects.filter(
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'changed_by')


class RoomStatusLogsByRoomView(generics.ListAPIView):
    """Get status history for a specific room."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    serializer_class = RoomStatusLogSerializer
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return RoomStatusLog.objects.filter(
            room_id=room_id,
            room__hotel=self.request.user.assigned_property
        ).select_related('room', 'changed_by').order_by('-changed_at')


class RoomConfigStatsView(APIView):
    """Get room configuration statistics."""
    permission_classes = [IsAuthenticated, IsFrontDeskOrAbove]
    
    def get(self, request):
        property_obj = request.user.assigned_property
        
        room_type_stats = RoomType.objects.filter(
            hotel=property_obj
        ).aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(is_active=True))
        )
        
        total_amenities = RoomAmenity.objects.count()
        
        total_images = RoomImage.objects.filter(
            room__hotel=property_obj
        ).count()
        
        # Room stats by type
        rooms_by_type = Room.objects.filter(
            hotel=property_obj
        ).values('room_type__name').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_room_types': room_type_stats['total'],
            'active_room_types': room_type_stats['active'],
            'total_amenities': total_amenities,
            'total_room_images': total_images,
            'rooms_by_type': list(rooms_by_type)
        })
