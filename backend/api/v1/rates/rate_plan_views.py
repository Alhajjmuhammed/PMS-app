"""
Views for Rates Management
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Avg, Min, Max
from datetime import datetime, timedelta
from decimal import Decimal

from apps.rates.models import RatePlan, RoomRate, DateRate, YieldRule
from apps.rooms.models import Room
from .rate_plan_serializers import (
    RatePlanSerializer,
    RatePlanDetailSerializer,
    RoomRateSerializer,
    DateRateSerializer,
    YieldRuleSerializer,
    BulkRoomRateSerializer,
    RateCalculationSerializer
)
from api.permissions import IsAdminOrManager


# ===== Rate Plans =====

class RatePlanListCreateView(generics.ListCreateAPIView):
    """List all rate plans or create new rate plan."""
    permission_classes = [IsAuthenticated]
    serializer_class = RatePlanSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_default', 'rate_type', 'meal_plan']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'priority', 'created_at']
    ordering = ['priority', 'name']
    
    def get_queryset(self):
        return RatePlan.objects.filter(
            property=self.request.user.property
        ).prefetch_related('room_rates')
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class RatePlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a rate plan."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RatePlanDetailSerializer
    
    def get_queryset(self):
        return RatePlan.objects.filter(
            property=self.request.user.property
        ).prefetch_related('room_rates__room_type')


class ActiveRatePlansView(generics.ListAPIView):
    """List only active rate plans."""
    permission_classes = [IsAuthenticated]
    serializer_class = RatePlanSerializer
    
    def get_queryset(self):
        return RatePlan.objects.filter(
            property=self.request.user.property,
            is_active=True
        ).order_by('priority', 'name')


# ===== Room Rates =====

class RoomRateListCreateView(generics.ListCreateAPIView):
    """List all room rates or create new room rate."""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomRateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rate_plan', 'room_type', 'is_active']
    ordering_fields = ['base_rate', 'created_at']
    ordering = ['room_type__name']
    
    def get_queryset(self):
        return RoomRate.objects.filter(
            property=self.request.user.property
        ).select_related('rate_plan', 'room_type')
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class RoomRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a room rate."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = RoomRateSerializer
    
    def get_queryset(self):
        return RoomRate.objects.filter(
            property=self.request.user.property
        ).select_related('rate_plan', 'room_type')


class RoomRateByPlanView(generics.ListAPIView):
    """Get all room rates for a specific rate plan."""
    permission_classes = [IsAuthenticated]
    serializer_class = RoomRateSerializer
    
    def get_queryset(self):
        rate_plan_id = self.kwargs.get('rate_plan_id')
        return RoomRate.objects.filter(
            property=self.request.user.property,
            rate_plan_id=rate_plan_id
        ).select_related('rate_plan', 'room_type')


class BulkRoomRateCreateView(APIView):
    """Create room rates for multiple room types at once."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request):
        serializer = BulkRoomRateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        rate_plan = data['rate_plan']
        room_types = data['room_types']
        
        created_rates = []
        for room_type in room_types:
            room_rate, created = RoomRate.objects.update_or_create(
                property=request.user.property,
                rate_plan=rate_plan,
                room_type=room_type,
                defaults={
                    'base_rate': data['base_rate'],
                    'extra_adult_rate': data.get('extra_adult_rate', 0),
                    'extra_child_rate': data.get('extra_child_rate', 0),
                    'weekend_rate': data.get('weekend_rate'),
                    'effective_from': data.get('effective_from'),
                    'effective_to': data.get('effective_to'),
                    'is_active': True
                }
            )
            created_rates.append(room_rate)
        
        response_serializer = RoomRateSerializer(created_rates, many=True)
        return Response({
            'message': f'Created/updated {len(created_rates)} room rates',
            'room_rates': response_serializer.data
        }, status=status.HTTP_201_CREATED)


# ===== Date Rates =====

class DateRateListCreateView(generics.ListCreateAPIView):
    """List all date rates or create new date rate."""
    permission_classes = [IsAuthenticated]
    serializer_class = DateRateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['room_type', 'is_closed']
    ordering_fields = ['date', 'rate']
    ordering = ['date']
    
    def get_queryset(self):
        queryset = DateRate.objects.filter(
            property=self.request.user.property
        ).select_related('room_type')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class DateRateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a date rate."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = DateRateSerializer
    
    def get_queryset(self):
        return DateRate.objects.filter(
            property=self.request.user.property
        ).select_related('room_type')


class DateRateByDateView(generics.ListAPIView):
    """Get date rates for a specific date."""
    permission_classes = [IsAuthenticated]
    serializer_class = DateRateSerializer
    
    def get_queryset(self):
        date_str = self.kwargs.get('date')
        return DateRate.objects.filter(
            property=self.request.user.property,
            date=date_str
        ).select_related('room_type')


# ===== Yield Rules =====

class YieldRuleListCreateView(generics.ListCreateAPIView):
    """List all yield rules or create new yield rule."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = YieldRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type', 'is_active', 'adjustment_type']
    search_fields = ['name']
    ordering_fields = ['priority', 'name', 'created_at']
    ordering = ['priority', 'name']
    
    def get_queryset(self):
        return YieldRule.objects.filter(
            property=self.request.user.property
        ).select_related('room_type')
    
    def perform_create(self, serializer):
        serializer.save(property=self.request.user.property)


class YieldRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a yield rule."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = YieldRuleSerializer
    
    def get_queryset(self):
        return YieldRule.objects.filter(
            property=self.request.user.property
        ).select_related('room_type')


class ActiveYieldRulesView(generics.ListAPIView):
    """List only active yield rules."""
    permission_classes = [IsAuthenticated]
    serializer_class = YieldRuleSerializer
    
    def get_queryset(self):
        return YieldRule.objects.filter(
            property=self.request.user.property,
            is_active=True
        ).select_related('room_type').order_by('priority')


# ===== Rate Calculation =====

class CalculateRateView(APIView):
    """Calculate rate for given dates and room type."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = RateCalculationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        room_type = data['room_type']
        check_in = data['check_in']
        check_out = data['check_out']
        adults = data.get('adults', 1)
        children = data.get('children', 0)
        rate_plan = data.get('rate_plan')
        
        # Calculate number of nights
        nights = (check_out - check_in).days
        
        # Get base rate
        if rate_plan:
            try:
                room_rate = RoomRate.objects.get(
                    property=request.user.property,
                    rate_plan=rate_plan,
                    room_type=room_type,
                    is_active=True
                )
                base_rate = room_rate.base_rate
                extra_adult = room_rate.extra_adult_rate
                extra_child = room_rate.extra_child_rate
            except RoomRate.DoesNotExist:
                return Response(
                    {'error': 'No rate found for this room type and rate plan'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Use default rate plan
            try:
                default_plan = RatePlan.objects.get(
                    property=request.user.property,
                    is_default=True,
                    is_active=True
                )
                room_rate = RoomRate.objects.get(
                    property=request.user.property,
                    rate_plan=default_plan,
                    room_type=room_type,
                    is_active=True
                )
                base_rate = room_rate.base_rate
                extra_adult = room_rate.extra_adult_rate
                extra_child = room_rate.extra_child_rate
            except (RatePlan.DoesNotExist, RoomRate.DoesNotExist):
                return Response(
                    {'error': 'No default rate found for this room type'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Calculate nightly rates considering date overrides
        daily_rates = []
        current_date = check_in
        
        while current_date < check_out:
            # Check for date-specific rate
            try:
                date_rate = DateRate.objects.get(
                    property=request.user.property,
                    room_type=room_type,
                    date=current_date
                )
                if date_rate.is_closed:
                    return Response(
                        {'error': f'Room type closed on {current_date}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                nightly_rate = date_rate.rate
            except DateRate.DoesNotExist:
                # Use base rate (check if weekend)
                if current_date.weekday() >= 5 and room_rate.weekend_rate:  # Saturday=5, Sunday=6
                    nightly_rate = room_rate.weekend_rate
                else:
                    nightly_rate = base_rate
            
            daily_rates.append({
                'date': current_date.isoformat(),
                'rate': float(nightly_rate)
            })
            current_date += timedelta(days=1)
        
        # Calculate total
        subtotal = sum(Decimal(str(rate['rate'])) for rate in daily_rates)
        
        # Add extra person charges
        extra_adults_count = max(0, adults - room_type.base_occupancy)
        extra_children_count = children
        
        extra_adult_total = extra_adult * extra_adults_count * nights
        extra_child_total = extra_child * extra_children_count * nights
        
        total = subtotal + extra_adult_total + extra_child_total
        
        # Apply yield rules if any
        # (Simplified - in production, calculate occupancy and apply rules)
        
        return Response({
            'room_type': room_type.name,
            'check_in': check_in,
            'check_out': check_out,
            'nights': nights,
            'adults': adults,
            'children': children,
            'daily_rates': daily_rates,
            'subtotal': float(subtotal),
            'extra_adult_charges': float(extra_adult_total),
            'extra_child_charges': float(extra_child_total),
            'total': float(total),
            'currency': 'USD',
            'rate_plan': rate_plan.name if rate_plan else 'Default'
        })


class RateStatsView(APIView):
    """Get rate statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        property_obj = request.user.property
        
        stats = RoomRate.objects.filter(
            property=property_obj,
            is_active=True
        ).aggregate(
            avg_rate=Avg('base_rate'),
            min_rate=Min('base_rate'),
            max_rate=Max('base_rate')
        )
        
        total_rate_plans = RatePlan.objects.filter(
            property=property_obj,
            is_active=True
        ).count()
        
        total_room_rates = RoomRate.objects.filter(
            property=property_obj,
            is_active=True
        ).count()
        
        return Response({
            'average_rate': float(stats['avg_rate']) if stats['avg_rate'] else 0,
            'minimum_rate': float(stats['min_rate']) if stats['min_rate'] else 0,
            'maximum_rate': float(stats['max_rate']) if stats['max_rate'] else 0,
            'total_rate_plans': total_rate_plans,
            'total_room_rates': total_room_rates
        })
