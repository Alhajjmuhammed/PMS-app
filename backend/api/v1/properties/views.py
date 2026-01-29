from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.properties.models import Property, SystemSetting
from api.permissions import CanManageProperties
from .serializers import PropertySerializer, SystemSettingSerializer


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
