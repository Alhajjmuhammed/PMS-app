from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.rates.models import RatePlan, Season, RoomRate
from api.permissions import IsAdminOrManager
from .serializers import RatePlanSerializer, SeasonSerializer, RoomRateSerializer


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


class RoomRateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
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


class SeasonDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = SeasonSerializer
    queryset = Season.objects.all()
