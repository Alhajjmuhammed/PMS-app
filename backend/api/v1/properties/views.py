from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.properties.models import Property, SystemSetting, Building, Floor
from api.permissions import CanManageProperties
from .serializers import (
    PropertySerializer, SystemSettingSerializer,
    BuildingSerializer, BuildingListSerializer, FloorSerializer
)


class PropertyListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, CanManageProperties]
    serializer_class = PropertySerializer
    
    def get_queryset(self):
        if self.request.user.assigned_property:
            return Property.objects.filter(pk=self.request.user.assigned_property.pk)
        return Property.objects.filter(is_active=True)


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, CanManageProperties]
    serializer_class = PropertySerializer
    queryset = Property.objects.all()


class SystemSettingView(APIView):
    """Get or update system settings."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get settings for user's property or global settings
        property_id = request.user.assigned_property_id if request.user.assigned_property else None
        
        try:
            settings = SystemSetting.objects.get(property_id=property_id)
        except SystemSetting.DoesNotExist:
            # Create default settings if they don't exist
            settings = SystemSetting.objects.create(property_id=property_id)
        
        serializer = SystemSettingSerializer(settings)
        return Response(serializer.data)
    
    def post(self, request):
        # Update settings for user's property or global settings
        property_id = request.user.assigned_property_id if request.user.assigned_property else None
        
        try:
            settings = SystemSetting.objects.get(property_id=property_id)
            serializer = SystemSettingSerializer(settings, data=request.data, partial=True)
        except SystemSetting.DoesNotExist:
            serializer = SystemSettingSerializer(data=request.data)
        
        if serializer.is_valid():
            if property_id and 'property' not in serializer.validated_data:
                serializer.save(property_id=property_id)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuildingListCreateView(generics.ListCreateAPIView):
    """List all buildings or create a new building."""
    permission_classes = [IsAuthenticated, CanManageProperties]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'property']
    ordering = ['property', 'name']
    
    def get_queryset(self):
        queryset = Building.objects.select_related('property')
        
        # Filter by user's property if assigned
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BuildingListSerializer
        return BuildingSerializer


class BuildingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a building."""
    permission_classes = [IsAuthenticated, CanManageProperties]
    serializer_class = BuildingSerializer
    
    def get_queryset(self):
        queryset = Building.objects.select_related('property').prefetch_related('building_floors')
        
        # Filter by user's property if assigned
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        
        return queryset


class FloorListCreateView(generics.ListCreateAPIView):
    """List all floors or create a new floor."""
    permission_classes = [IsAuthenticated, CanManageProperties]
    serializer_class = FloorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['building']
    ordering_fields = ['number', 'building']
    ordering = ['building', 'number']
    
    def get_queryset(self):
        queryset = Floor.objects.select_related('building', 'building__property')
        
        # Filter by user's property if assigned
        if self.request.user.assigned_property:
            queryset = queryset.filter(building__property=self.request.user.assigned_property)
        
        return queryset


class FloorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a floor."""
    permission_classes = [IsAuthenticated, CanManageProperties]
    serializer_class = FloorSerializer
    
    def get_queryset(self):
        queryset = Floor.objects.select_related('building', 'building__property')
        
        # Filter by user's property if assigned
        if self.request.user.assigned_property:
            queryset = queryset.filter(building__property=self.request.user.assigned_property)
        
        return queryset
