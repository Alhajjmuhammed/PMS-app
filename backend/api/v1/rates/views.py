from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.rates.models import RatePlan, Season, RoomRate, DateRate
from api.permissions import IsAdminOrManager
from .serializers import (
    RatePlanSerializer, SeasonSerializer, 
    RoomRateSerializer, DateRateSerializer
)


class RatePlanListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RatePlanSerializer
    
    def get_queryset(self):
        queryset = RatePlan.objects.filter(is_active=True)
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def perform_create(self, serializer):
        if self.request.user.assigned_property and 'property' not in serializer.validated_data:
            serializer.save(property=self.request.user.assigned_property)
        else:
            serializer.save()


class RatePlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RatePlanSerializer
    queryset = RatePlan.objects.all()


class SeasonListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = SeasonSerializer
    
    def get_queryset(self):
        queryset = Season.objects.filter(is_active=True)
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset.order_by('start_date')
    
    def perform_create(self, serializer):
        if self.request.user.assigned_property and 'property' not in serializer.validated_data:
            serializer.save(property=self.request.user.assigned_property)
        else:
            serializer.save()


class RoomRateListCreateView(generics.ListCreateAPIView):
    """List all room rates or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomRateSerializer
    
    def get_queryset(self):
        queryset = RoomRate.objects.select_related(
            'rate_plan', 'room_type', 'season'
        ).filter(is_active=True)
        
        rate_plan_id = self.request.query_params.get('rate_plan')
        room_type_id = self.request.query_params.get('room_type')
        season_id = self.request.query_params.get('season')
        
        if rate_plan_id:
            queryset = queryset.filter(rate_plan_id=rate_plan_id)
        if room_type_id:
            queryset = queryset.filter(room_type_id=room_type_id)
        if season_id:
            queryset = queryset.filter(season_id=season_id)
        
        return queryset.order_by('rate_plan__name', 'room_type__name')


class RoomRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room rate."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomRateSerializer
    queryset = RoomRate.objects.select_related('rate_plan', 'room_type', 'season')


class DateRateListCreateView(generics.ListCreateAPIView):
    """List or create date-specific rate overrides."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = DateRateSerializer
    
    def get_queryset(self):
        queryset = DateRate.objects.select_related('room_type', 'rate_plan')
        
        room_type_id = self.request.query_params.get('room_type')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if room_type_id:
            queryset = queryset.filter(room_type_id=room_type_id)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset.order_by('date')


class DateRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a date rate."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = DateRateSerializer
    queryset = DateRate.objects.select_related('room_type', 'rate_plan')


class SeasonDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = SeasonSerializer
    queryset = Season.objects.all()
