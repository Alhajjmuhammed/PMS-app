from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.properties.models import Property
from .serializers import PropertySerializer


class PropertyListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PropertySerializer
    
    def get_queryset(self):
        if self.request.user.assigned_property:
            return Property.objects.filter(pk=self.request.user.assigned_property.pk)
        return Property.objects.filter(is_active=True)


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PropertySerializer
    queryset = Property.objects.all()
