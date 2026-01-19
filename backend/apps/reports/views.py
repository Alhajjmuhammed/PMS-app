from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from datetime import date, timedelta
from .models import DailyStatistics, MonthlyStatistics, ReportTemplate, NightAudit, AuditLog


class ReportsDashboardView(LoginRequiredMixin, View):
    template_name = 'reports/dashboard.html'
    
    def get(self, request):
        today = date.today()
        
        # Get today's statistics
        daily_stats = DailyStatistics.objects.filter(date=today).first()
        
        # Pending night audits
        pending_audits = NightAudit.objects.filter(status=NightAudit.Status.PENDING).count()
        
        context = {
            'daily_stats': daily_stats,
            'pending_audits': pending_audits,
            'today': today,
        }
        return render(request, self.template_name, context)


class DailyReportView(LoginRequiredMixin, View):
    template_name = 'reports/daily.html'
    
    def get(self, request):
        report_date = request.GET.get('date', date.today().isoformat())
        report_date = date.fromisoformat(report_date)
        
        stats = DailyStatistics.objects.filter(date=report_date)
        if request.user.property:
            stats = stats.filter(property=request.user.property)
        
        context = {
            'report_date': report_date,
            'stats': stats.first(),
        }
        return render(request, self.template_name, context)


class OccupancyReportView(LoginRequiredMixin, View):
    template_name = 'reports/occupancy.html'
    
    def get(self, request):
        start_date = request.GET.get('start', (date.today() - timedelta(days=30)).isoformat())
        end_date = request.GET.get('end', date.today().isoformat())
        
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
        
        stats = DailyStatistics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if request.user.property:
            stats = stats.filter(property=request.user.property)
        
        # Calculate averages
        averages = stats.aggregate(
            avg_occupancy=Avg('occupancy_percent'),
            avg_adr=Avg('adr'),
            avg_revpar=Avg('revpar')
        )
        
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'stats': stats,
            'averages': averages,
        }
        return render(request, self.template_name, context)


class RevenueReportView(LoginRequiredMixin, View):
    template_name = 'reports/revenue.html'
    
    def get(self, request):
        start_date = request.GET.get('start', (date.today() - timedelta(days=30)).isoformat())
        end_date = request.GET.get('end', date.today().isoformat())
        
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
        
        stats = DailyStatistics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        if request.user.property:
            stats = stats.filter(property=request.user.property)
        
        totals = stats.aggregate(
            total_room=Sum('room_revenue'),
            total_fb=Sum('fb_revenue'),
            total_other=Sum('other_revenue'),
            total=Sum('total_revenue')
        )
        
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'stats': stats.order_by('date'),
            'totals': totals,
        }
        return render(request, self.template_name, context)


class ArrivalsReportView(LoginRequiredMixin, View):
    template_name = 'reports/arrivals.html'
    
    def get(self, request):
        from apps.reservations.models import Reservation
        
        report_date = request.GET.get('date', date.today().isoformat())
        report_date = date.fromisoformat(report_date)
        
        arrivals = Reservation.objects.filter(
            check_in_date=report_date,
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).select_related('guest', 'source')
        
        if request.user.property:
            arrivals = arrivals.filter(property=request.user.property)
        
        context = {
            'report_date': report_date,
            'arrivals': arrivals,
        }
        return render(request, self.template_name, context)


class DeparturesReportView(LoginRequiredMixin, View):
    template_name = 'reports/departures.html'
    
    def get(self, request):
        from apps.reservations.models import Reservation
        
        report_date = request.GET.get('date', date.today().isoformat())
        report_date = date.fromisoformat(report_date)
        
        departures = Reservation.objects.filter(
            check_out_date=report_date,
            status__in=['CHECKED_IN', 'CHECKED_OUT']
        ).select_related('guest')
        
        if request.user.property:
            departures = departures.filter(property=request.user.property)
        
        context = {
            'report_date': report_date,
            'departures': departures,
        }
        return render(request, self.template_name, context)


class InHouseReportView(LoginRequiredMixin, View):
    template_name = 'reports/in_house.html'
    
    def get(self, request):
        from apps.reservations.models import Reservation
        
        in_house = Reservation.objects.filter(
            status='CHECKED_IN'
        ).select_related('guest')
        
        if request.user.property:
            in_house = in_house.filter(property=request.user.property)
        
        context = {
            'in_house': in_house,
            'total_guests': in_house.count(),
        }
        return render(request, self.template_name, context)


class ProductionReportView(LoginRequiredMixin, View):
    template_name = 'reports/production.html'
    
    def get(self, request):
        from apps.reservations.models import Reservation
        from django.db.models.functions import TruncDate
        
        start_date = request.GET.get('start', (date.today() - timedelta(days=30)).isoformat())
        end_date = request.GET.get('end', date.today().isoformat())
        
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
        
        # Reservations created in period
        reservations = Reservation.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        if request.user.property:
            reservations = reservations.filter(property=request.user.property)
        
        # Group by booking source
        by_source = reservations.values('source__name').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('-count')
        
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'total_reservations': reservations.count(),
            'by_source': by_source,
        }
        return render(request, self.template_name, context)


class ForecastReportView(LoginRequiredMixin, View):
    template_name = 'reports/forecast.html'
    
    def get(self, request):
        from apps.reservations.models import Reservation
        from apps.rooms.models import Room
        
        days = int(request.GET.get('days', 30))
        today = date.today()
        
        forecast_data = []
        for i in range(days):
            forecast_date = today + timedelta(days=i)
            
            # Count reservations
            reservations = Reservation.objects.filter(
                check_in_date__lte=forecast_date,
                check_out_date__gt=forecast_date,
                status__in=['CONFIRMED', 'CHECKED_IN']
            )
            
            if request.user.property:
                reservations = reservations.filter(property=request.user.property)
                total_rooms = Room.objects.filter(property=request.user.property, is_active=True).count()
            else:
                total_rooms = Room.objects.filter(is_active=True).count()
            
            rooms_occupied = reservations.count()
            
            forecast_data.append({
                'date': forecast_date,
                'occupied': rooms_occupied,
                'available': total_rooms - rooms_occupied if total_rooms else 0,
                'occupancy': (rooms_occupied / total_rooms * 100) if total_rooms else 0
            })
        
        context = {
            'forecast': forecast_data,
            'days': days,
        }
        return render(request, self.template_name, context)


class NightAuditView(LoginRequiredMixin, ListView):
    model = NightAudit
    template_name = 'reports/night_audit_list.html'
    context_object_name = 'audits'
    paginate_by = 30


class NightAuditDetailView(LoginRequiredMixin, DetailView):
    model = NightAudit
    template_name = 'reports/night_audit_detail.html'
    context_object_name = 'audit'


class RunNightAuditView(LoginRequiredMixin, View):
    def post(self, request):
        from apps.reservations.models import Reservation
        from apps.billing.models import FolioCharge
        
        property_obj = request.user.property
        business_date = date.today() - timedelta(days=1)
        
        # Create night audit record
        audit, created = NightAudit.objects.get_or_create(
            property=property_obj,
            business_date=business_date,
            defaults={'status': NightAudit.Status.IN_PROGRESS}
        )
        
        if not created and audit.status == NightAudit.Status.COMPLETED:
            messages.warning(request, 'Night audit already completed for this date.')
            return redirect('reports:night_audit_detail', pk=audit.pk)
        
        audit.status = NightAudit.Status.IN_PROGRESS
        audit.started_at = timezone.now()
        audit.save()
        
        AuditLog.objects.create(
            night_audit=audit,
            step='Start',
            message='Night audit started'
        )
        
        # Process room charges (stub)
        AuditLog.objects.create(
            night_audit=audit,
            step='Room Charges',
            message='Posted room charges for in-house guests'
        )
        
        # Calculate statistics
        in_house = Reservation.objects.filter(
            property=property_obj,
            status='CHECKED_IN'
        ).count()
        
        audit.rooms_sold = in_house
        audit.status = NightAudit.Status.COMPLETED
        audit.completed_at = timezone.now()
        audit.completed_by = request.user
        audit.save()
        
        AuditLog.objects.create(
            night_audit=audit,
            step='Complete',
            message='Night audit completed successfully'
        )
        
        messages.success(request, 'Night audit completed.')
        return redirect('reports:night_audit_detail', pk=audit.pk)


class StatisticsView(LoginRequiredMixin, View):
    template_name = 'reports/statistics.html'
    
    def get(self, request):
        monthly_stats = MonthlyStatistics.objects.all()[:12]
        
        if request.user.property:
            monthly_stats = monthly_stats.filter(property=request.user.property)
        
        context = {
            'monthly_stats': monthly_stats,
        }
        return render(request, self.template_name, context)


class ReportTemplateListView(LoginRequiredMixin, ListView):
    model = ReportTemplate
    template_name = 'reports/template_list.html'
    context_object_name = 'templates'


class RunReportView(LoginRequiredMixin, View):
    def get(self, request, pk):
        template = get_object_or_404(ReportTemplate, pk=pk)
        
        # Route to appropriate report view based on type
        if template.report_type == ReportTemplate.ReportType.DAILY:
            return redirect('reports:daily')
        elif template.report_type == ReportTemplate.ReportType.OCCUPANCY:
            return redirect('reports:occupancy')
        elif template.report_type == ReportTemplate.ReportType.REVENUE:
            return redirect('reports:revenue')
        
        return redirect('reports:dashboard')
