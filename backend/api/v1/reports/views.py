from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count
from datetime import date, timedelta
from apps.reports.models import DailyStatistics
from apps.reservations.models import Reservation
from apps.rooms.models import Room
from apps.billing.models import Payment
from api.permissions import IsAdminOrManager


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
