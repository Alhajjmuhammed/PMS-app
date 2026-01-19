from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.rates.models import RatePlan, Season, RoomRate
from .serializers import RatePlanSerializer, SeasonSerializer, RoomRateSerializer


class RatePlanListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatePlanSerializer
    
    def get_queryset(self):
        queryset = RatePlan.objects.filter(is_active=True)
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset


class RatePlanDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RatePlanSerializer
    queryset = RatePlan.objects.all()


class SeasonListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SeasonSerializer
    
    def get_queryset(self):
        queryset = Season.objects.filter(is_active=True)
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset.order_by('start_date')


class RoomRateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomRateSerializer
    
    def get_queryset(self):
        queryset = RoomRate.objects.filter(is_active=True)
        rate_plan_id = self.request.query_params.get('rate_plan')
        room_type_id = self.request.query_params.get('room_type')
        
        if rate_plan_id:
            queryset = queryset.filter(rate_plan_id=rate_plan_id)
        if room_type_id:
            queryset = queryset.filter(room_type_id=room_type_id)
            
        return queryset
