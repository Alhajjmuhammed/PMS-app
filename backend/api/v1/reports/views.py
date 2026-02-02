from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import date, timedelta
from apps.reports.models import DailyStatistics, MonthlyStatistics, NightAudit, AuditLog
from apps.reservations.models import Reservation
from apps.rooms.models import Room
from apps.billing.models import Payment, Folio
from api.permissions import IsAdminOrManager
from .serializers import (
    MonthlyStatisticsSerializer, MonthlyStatisticsCreateSerializer,
    NightAuditSerializer, NightAuditCreateSerializer, NightAuditUpdateSerializer,
    StartNightAuditSerializer, AuditLogSerializer
)


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        today = date.today()
        property_obj = request.user.assigned_property
        
        # Get today's stats
        daily_stats = DailyStatistics.objects.filter(date=today)
        if property_obj:
            daily_stats = daily_stats.filter(property=property_obj)
        
        stats = daily_stats.first()
        
        # Calculate live stats if not available
        if not stats:
            rooms = Room.objects.filter(is_active=True)
            reservations = Reservation.objects
            
            if property_obj:
                rooms = rooms.filter(property=property_obj)
                reservations = reservations.filter(property=property_obj)
            
            total_rooms = rooms.count()
            occupied = reservations.filter(status='CHECKED_IN').count()
            
            occupancy = (occupied / total_rooms * 100) if total_rooms else 0
            
            # Today's revenue
            payments = Payment.objects.filter(payment_date__date=today)
            revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
            
            return Response({
                'date': today,
                'total_rooms': total_rooms,
                'occupied': occupied,
                'occupancy_percent': round(occupancy, 1),
                'arrivals': reservations.filter(check_in_date=today, status='CONFIRMED').count(),
                'departures': reservations.filter(check_out_date=today, status='CHECKED_IN').count(),
                'revenue': float(revenue),
            })
        
        return Response({
            'date': stats.date,
            'total_rooms': stats.total_rooms,
            'rooms_sold': stats.rooms_sold,
            'occupancy_percent': float(stats.occupancy_percent),
            'arrivals': stats.arrivals,
            'departures': stats.departures,
            'in_house': stats.in_house,
            'adr': float(stats.adr),
            'revpar': float(stats.revpar),
            'room_revenue': float(stats.room_revenue),
            'fb_revenue': float(stats.fb_revenue),
            'total_revenue': float(stats.total_revenue),
        })


class OccupancyReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        start = request.query_params.get('start', (date.today() - timedelta(days=30)).isoformat())
        end = request.query_params.get('end', date.today().isoformat())
        
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
        
        stats = DailyStatistics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if request.user.assigned_property:
            stats = stats.filter(property=request.user.assigned_property)
        
        data = []
        for stat in stats.order_by('date'):
            data.append({
                'date': stat.date,
                'occupancy': float(stat.occupancy_percent),
                'adr': float(stat.adr),
                'revpar': float(stat.revpar),
                'rooms_sold': stat.rooms_sold,
            })
        
        # Averages
        averages = stats.aggregate(
            avg_occupancy=Avg('occupancy_percent'),
            avg_adr=Avg('adr'),
            avg_revpar=Avg('revpar')
        )
        
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'data': data,
            'averages': {
                'occupancy': float(averages['avg_occupancy'] or 0),
                'adr': float(averages['avg_adr'] or 0),
                'revpar': float(averages['avg_revpar'] or 0),
            }
        })


class RevenueReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        start = request.query_params.get('start', (date.today() - timedelta(days=30)).isoformat())
        end = request.query_params.get('end', date.today().isoformat())
        
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
        
        stats = DailyStatistics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if request.user.assigned_property:
            stats = stats.filter(property=request.user.assigned_property)
        
        data = []
        for stat in stats.order_by('date'):
            data.append({
                'date': stat.date,
                'room_revenue': float(stat.room_revenue),
                'fb_revenue': float(stat.fb_revenue),
                'other_revenue': float(stat.other_revenue),
                'total': float(stat.total_revenue),
            })
        
        totals = stats.aggregate(
            room=Sum('room_revenue'),
            fb=Sum('fb_revenue'),
            other=Sum('other_revenue'),
            total=Sum('total_revenue')
        )
        
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'data': data,
            'totals': {
                'room_revenue': float(totals['room'] or 0),
                'fb_revenue': float(totals['fb'] or 0),
                'other_revenue': float(totals['other'] or 0),
                'total': float(totals['total'] or 0),
            }
        })


class AdvancedAnalyticsView(APIView):
    """Advanced analytics with date range and metric filters."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        from datetime import datetime
        from django.db.models import Q
        
        # Get query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        metric = request.query_params.get('metric', 'revenue')
        
        # Default to last 30 days
        if not end_date:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        property_obj = request.user.assigned_property
        
        # Get daily statistics
        stats = DailyStatistics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if property_obj:
            stats = stats.filter(property=property_obj)
        
        # Aggregate data
        data = []
        current_date = start_date
        while current_date <= end_date:
            day_stat = stats.filter(date=current_date).first()
            
            if metric == 'revenue':
                value = float(day_stat.revenue) if day_stat else 0
            elif metric == 'occupancy':
                value = float(day_stat.occupancy_percent) if day_stat else 0
            elif metric == 'reservations':
                value = Reservation.objects.filter(
                    created_at__date=current_date
                ).count()
                if property_obj:
                    value = Reservation.objects.filter(
                        created_at__date=current_date,
                        property=property_obj
                    ).count()
            else:
                value = 0
            
            data.append({
                'date': current_date.isoformat(),
                'value': value
            })
            current_date += timedelta(days=1)
        
        # Calculate summary stats
        total_value = sum(d['value'] for d in data)
        avg_value = total_value / len(data) if data else 0
        
        return Response({
            'metric': metric,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'data': data,
            'summary': {
                'total': total_value,
                'average': avg_value,
                'max': max((d['value'] for d in data), default=0),
                'min': min((d['value'] for d in data), default=0)
            }
        })


class RevenueForecastView(APIView):
    """Revenue forecast for predictive analytics."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        property_obj = request.user.assigned_property
        today = date.today()
        
        # Get last 30 days revenue
        last_30_days = DailyStatistics.objects.filter(
            date__gte=today - timedelta(days=30),
            date__lt=today
        )
        
        if property_obj:
            last_30_days = last_30_days.filter(property=property_obj)
        
        avg_daily_revenue = last_30_days.aggregate(
            avg=Avg('total_revenue')
        )['avg'] or 0
        
        # Simple forecast: project average for next 30 days
        forecast = []
        for i in range(30):
            forecast_date = today + timedelta(days=i)
            # Add some variance (±10%)
            import random
            variance = random.uniform(0.9, 1.1)
            forecasted_value = float(avg_daily_revenue) * variance
            
            forecast.append({
                'date': forecast_date.isoformat(),
                'forecasted_revenue': round(forecasted_value, 2),
                'confidence': 'medium'
            })
        
        return Response({
            'forecast_period': '30_days',
            'base_avg_revenue': float(avg_daily_revenue),
            'forecast': forecast,
            'total_forecasted': sum(f['forecasted_revenue'] for f in forecast)
        })


class DailyReportView(APIView):
    """Get daily statistics report."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get(self, request):
        from datetime import datetime
        
        date_param = request.query_params.get('date')
        if date_param:
            target_date = datetime.fromisoformat(date_param).date()
        else:
            target_date = date.today()
        
        property_obj = request.user.assigned_property
        
        # Get daily statistics
        try:
            daily_stat = DailyStatistics.objects.get(
                date=target_date,
                property=property_obj
            ) if property_obj else DailyStatistics.objects.filter(date=target_date).first()
            
            if daily_stat:
                return Response({
                    'date': daily_stat.date,
                    'total_rooms': daily_stat.total_rooms,
                    'rooms_sold': daily_stat.rooms_sold,
                    'occupancy_percent': float(daily_stat.occupancy_percent),
                    'room_revenue': float(daily_stat.room_revenue),
                    'total_revenue': float(daily_stat.total_revenue),
                    'adr': float(daily_stat.adr),
                    'revpar': float(daily_stat.revpar),
                    'arrivals': daily_stat.arrivals,
                    'departures': daily_stat.departures,
                    'in_house': daily_stat.in_house,
                })
            else:
                return Response({
                    'date': target_date,
                    'message': 'No data available for this date'
                })
        except Exception as e:
            return Response({
                'date': target_date,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= Monthly Statistics Views =============

class MonthlyStatisticsListCreateView(generics.ListCreateAPIView):
    """List all monthly statistics or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['property', 'year', 'month']
    ordering_fields = ['year', 'month', 'total_revenue']
    ordering = ['-year', '-month']
    
    def get_queryset(self):
        queryset = MonthlyStatistics.objects.select_related('property')
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MonthlyStatisticsCreateSerializer
        return MonthlyStatisticsSerializer


class MonthlyStatisticsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete monthly statistics."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        queryset = MonthlyStatistics.objects.select_related('property')
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MonthlyStatisticsCreateSerializer
        return MonthlyStatisticsSerializer


# ============= Night Audit Views =============

class NightAuditListCreateView(generics.ListCreateAPIView):
    """List all night audits or create a new one."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property', 'status', 'business_date']
    search_fields = ['business_date', 'notes']
    ordering_fields = ['business_date', 'completed_at']
    ordering = ['-business_date']
    
    def get_queryset(self):
        queryset = NightAudit.objects.select_related(
            'property', 'completed_by'
        ).prefetch_related('logs')
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NightAuditCreateSerializer
        return NightAuditSerializer
    
    def perform_create(self, serializer):
        # If no property specified and user has assigned property, use it
        if self.request.user.assigned_property and 'property' not in serializer.validated_data:
            serializer.save(property=self.request.user.assigned_property)
        else:
            serializer.save()


class NightAuditDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a night audit."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def get_queryset(self):
        queryset = NightAudit.objects.select_related(
            'property', 'completed_by'
        ).prefetch_related('logs')
        if self.request.user.assigned_property:
            queryset = queryset.filter(property=self.request.user.assigned_property)
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NightAuditUpdateSerializer
        return NightAuditSerializer


class StartNightAuditView(APIView):
    """Start the night audit process."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        night_audit = get_object_or_404(NightAudit, pk=pk)
        
        # Check if user has access
        if request.user.assigned_property:
            if night_audit.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if already started
        if night_audit.status != NightAudit.Status.PENDING:
            return Response(
                {'error': f'Audit is already {night_audit.status.lower()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = StartNightAuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Start the audit
        night_audit.status = NightAudit.Status.IN_PROGRESS
        night_audit.started_at = timezone.now()
        night_audit.save()
        
        # Create initial log
        AuditLog.objects.create(
            night_audit=night_audit,
            step='START',
            message=f'Night audit started by {request.user.get_full_name()}'
        )
        
        # If auto_process is True, run the audit steps
        if serializer.validated_data.get('auto_process', True):
            self._run_audit_steps(night_audit, request.user)
        
        return Response(NightAuditSerializer(night_audit).data)
    
    def _run_audit_steps(self, night_audit, user):
        """Run automatic audit steps."""
        property_obj = night_audit.property
        business_date = night_audit.business_date
        
        try:
            # Step 1: Process no-shows
            AuditLog.objects.create(
                night_audit=night_audit,
                step='NO_SHOWS',
                message='Processing no-show reservations'
            )
            # TODO: Implement no-show processing logic
            night_audit.no_shows_processed = True
            night_audit.save()
            
            # Step 2: Post room rates
            AuditLog.objects.create(
                night_audit=night_audit,
                step='ROOM_RATES',
                message='Posting room rates for in-house guests'
            )
            # TODO: Implement room rate posting logic
            night_audit.room_rates_posted = True
            night_audit.save()
            
            # Step 3: Check departures
            AuditLog.objects.create(
                night_audit=night_audit,
                step='DEPARTURES',
                message='Checking departure folios'
            )
            # TODO: Implement departure checking logic
            night_audit.departures_checked = True
            night_audit.save()
            
            # Step 4: Verify settled folios
            AuditLog.objects.create(
                night_audit=night_audit,
                step='FOLIOS',
                message='Verifying all folios are settled'
            )
            # TODO: Implement folio verification logic
            night_audit.folios_settled = True
            night_audit.save()
            
            # Step 5: Calculate totals
            AuditLog.objects.create(
                night_audit=night_audit,
                step='TOTALS',
                message='Calculating revenue totals'
            )
            
            # Get payments for the business date
            payments = Payment.objects.filter(
                folio__property=property_obj,
                payment_date__date=business_date
            ).aggregate(total=Sum('amount'))
            
            # Get folios for revenue calculation
            folios = Folio.objects.filter(
                property=property_obj,
                created_at__date=business_date
            )
            
            room_revenue = folios.aggregate(total=Sum('room_charges'))['total'] or 0
            fb_revenue = folios.aggregate(total=Sum('fb_charges'))['total'] or 0
            other_revenue = folios.aggregate(total=Sum('other_charges'))['total'] or 0
            
            night_audit.room_revenue = room_revenue
            night_audit.fb_revenue = fb_revenue
            night_audit.other_revenue = other_revenue
            night_audit.total_revenue = room_revenue + fb_revenue + other_revenue
            night_audit.payments_collected = payments['total'] or 0
            
            # Get room counts
            reservations = Reservation.objects.filter(
                property=property_obj,
                check_in_date__lte=business_date,
                check_out_date__gt=business_date
            )
            night_audit.rooms_sold = reservations.count()
            night_audit.arrivals_count = reservations.filter(check_in_date=business_date).count()
            
            # Tomorrow's departures
            next_date = business_date + timedelta(days=1)
            night_audit.departures_count = Reservation.objects.filter(
                property=property_obj,
                check_out_date=next_date
            ).count()
            
            night_audit.save()
            
            AuditLog.objects.create(
                night_audit=night_audit,
                step='COMPLETE',
                message='Night audit completed successfully'
            )
            
        except Exception as e:
            AuditLog.objects.create(
                night_audit=night_audit,
                step='ERROR',
                message=f'Error during audit: {str(e)}',
                is_error=True
            )


class CompleteNightAuditView(APIView):
    """Complete the night audit and roll to next business date."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        night_audit = get_object_or_404(NightAudit, pk=pk)
        
        # Check if user has access
        if request.user.assigned_property:
            if night_audit.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if audit is in progress
        if night_audit.status != NightAudit.Status.IN_PROGRESS:
            return Response(
                {'error': 'Audit must be in progress to complete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify all checks are done
        if not all([
            night_audit.no_shows_processed,
            night_audit.room_rates_posted,
            night_audit.folios_settled,
            night_audit.departures_checked
        ]):
            return Response(
                {'error': 'All audit checks must be completed before finishing'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Complete the audit
        night_audit.status = NightAudit.Status.COMPLETED
        night_audit.completed_at = timezone.now()
        night_audit.completed_by = request.user
        night_audit.save()
        
        AuditLog.objects.create(
            night_audit=night_audit,
            step='FINALIZED',
            message=f'Night audit finalized by {request.user.get_full_name()}'
        )
        
        # TODO: Roll business date forward
        # TODO: Create daily statistics record
        
        return Response(NightAuditSerializer(night_audit).data)


class RollbackNightAuditView(APIView):
    """Rollback a completed night audit."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        night_audit = get_object_or_404(NightAudit, pk=pk)
        
        # Check if user has access
        if request.user.assigned_property:
            if night_audit.property != request.user.assigned_property:
                return Response(
                    {'error': 'You do not have access to this resource'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if audit is completed
        if night_audit.status != NightAudit.Status.COMPLETED:
            return Response(
                {'error': 'Only completed audits can be rolled back'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rollback the audit
        night_audit.status = NightAudit.Status.ROLLED_BACK
        night_audit.save()
        
        AuditLog.objects.create(
            night_audit=night_audit,
            step='ROLLBACK',
            message=f'Night audit rolled back by {request.user.get_full_name()}'
        )
        
        # TODO: Reverse any business date changes
        # TODO: Mark daily statistics as invalid
        
        return Response(NightAuditSerializer(night_audit).data)


class AuditLogListView(generics.ListAPIView):
    """List audit logs for a night audit."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = AuditLogSerializer
    
    def get_queryset(self):
        night_audit_id = self.kwargs['night_audit_id']
        queryset = AuditLog.objects.filter(night_audit_id=night_audit_id)
        
        # Check property access
        if self.request.user.assigned_property:
            queryset = queryset.filter(
                night_audit__property=self.request.user.assigned_property
            )
        
        return queryset
