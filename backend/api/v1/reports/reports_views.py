"""
Views for Reports Module
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Count, Avg, Sum
from datetime import date, timedelta

from apps.reports.models import (
    DailyStatistics, MonthlyStatistics, ReportTemplate, NightAudit, AuditLog
)
from .reports_serializers import (
    DailyStatisticsSerializer,
    MonthlyStatisticsSerializer,
    ReportTemplateSerializer,
    NightAuditSerializer,
    AuditLogSerializer,
    NightAuditSummarySerializer,
    GenerateReportSerializer
)
from api.permissions import IsAdminOrManager


# ===== Daily Statistics =====

class DailyStatisticsListCreateView(generics.ListCreateAPIView):
    """List all daily statistics or create new entry."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = DailyStatisticsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property']
    ordering_fields = ['date']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = DailyStatistics.objects.filter(
            property=getattr(self.request.user, 'property', None)
        ).select_related('property')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(property=getattr(self.request.user, 'property', None))


class DailyStatisticsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete daily statistics."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = DailyStatisticsSerializer
    
    def get_queryset(self):
        return DailyStatistics.objects.filter(
            property=getattr(self.request.user, 'property', None)
        ).select_related('property')


class DailyStatisticsByDateView(generics.RetrieveAPIView):
    """Get daily statistics for a specific date."""
    permission_classes = [IsAuthenticated]
    serializer_class = DailyStatisticsSerializer
    lookup_field = 'date'
    
    def get_queryset(self):
        return DailyStatistics.objects.filter(
            property=getattr(self.request.user, 'property', None)
        ).select_related('property')


# ===== Monthly Statistics =====

class MonthlyStatisticsListCreateView(generics.ListCreateAPIView):
    """List all monthly statistics or create new entry."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = MonthlyStatisticsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'year']
    ordering_fields = ['year', 'month']
    ordering = ['-year', '-month']
    
    def get_queryset(self):
        return MonthlyStatistics.objects.filter(
            property=getattr(self.request.user, 'property', None)
        ).select_related('property')
    
    def perform_create(self, serializer):
        serializer.save(property=getattr(self.request.user, 'property', None))


class MonthlyStatisticsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete monthly statistics."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = MonthlyStatisticsSerializer
    
    def get_queryset(self):
        return MonthlyStatistics.objects.filter(
            property=getattr(self.request.user, 'property', None)
        ).select_related('property')


# ===== Report Templates =====

class ReportTemplateListCreateView(generics.ListCreateAPIView):
    """List all report templates or create new template."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReportTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_scheduled']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        return ReportTemplate.objects.filter(
            Q(property=getattr(self.request.user, 'property', None)) | Q(property__isnull=True)
        ).select_related('property', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(
            property=getattr(self.request.user, 'property', None),
            created_by=self.request.user
        )


class ReportTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a report template."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReportTemplateSerializer
    
    def get_queryset(self):
        return ReportTemplate.objects.filter(
            Q(property=getattr(self.request.user, 'property', None)) | Q(property__isnull=True)
        ).select_related('property', 'created_by')


class GenerateReportView(APIView):
    """Generate a report based on template or parameters."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = GenerateReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # In real implementation, this would generate actual report data
        # based on report type and parameters
        report_data = {
            'report_type': data['report_type'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'generated_at': date.today(),
            'message': 'Report generated successfully'
        }
        
        return Response(report_data)


# ===== Night Audit =====

class NightAuditListCreateView(generics.ListCreateAPIView):
    """List all night audits or create new audit."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = NightAuditSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['audit_date']
    ordering = ['-audit_date']
    
    def get_queryset(self):
        queryset = NightAudit.objects.filter(
            property=getattr(self.request.user, 'property', None)
        ).select_related('property', 'completed_by').prefetch_related('logs')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(audit_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(audit_date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(property=getattr(self.request.user, 'property', None))


class NightAuditDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a night audit."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    serializer_class = NightAuditSerializer
    
    def get_queryset(self):
        return NightAudit.objects.filter(
            property=getattr(self.request.user, 'property', None)
        ).select_related('property', 'completed_by').prefetch_related('logs')


class PendingNightAuditsView(generics.ListAPIView):
    """List pending night audits."""
    permission_classes = [IsAuthenticated]
    serializer_class = NightAuditSerializer
    
    def get_queryset(self):
        return NightAudit.objects.filter(
            property=getattr(self.request.user, 'property', None),
            status='PENDING'
        ).select_related('property').order_by('audit_date')


class StartNightAuditView(APIView):
    """Start a night audit process."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        try:
            from django.utils import timezone
            audit = NightAudit.objects.get(
                pk=pk,
                property=request.user.property
            )
            
            if audit.status != 'PENDING':
                return Response(
                    {'error': 'Audit is not in pending status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            audit.status = 'IN_PROGRESS'
            audit.started_at = timezone.now()
            audit.save()
            
            # Create log entry
            AuditLog.objects.create(
                night_audit=audit,
                action='Audit Started',
                details=f'Started by {request.user.get_full_name()}',
                success=True
            )
            
            serializer = NightAuditSerializer(audit)
            return Response(serializer.data)
            
        except NightAudit.DoesNotExist:
            return Response(
                {'error': 'Night audit not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CompleteNightAuditView(APIView):
    """Complete a night audit process."""
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    
    def post(self, request, pk):
        try:
            from django.utils import timezone
            audit = NightAudit.objects.get(
                pk=pk,
                property=request.user.property
            )
            
            if audit.status != 'IN_PROGRESS':
                return Response(
                    {'error': 'Audit is not in progress'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            audit.status = 'COMPLETED'
            audit.completed_at = timezone.now()
            audit.completed_by = request.user
            audit.save()
            
            # Create log entry
            AuditLog.objects.create(
                night_audit=audit,
                action='Audit Completed',
                details=f'Completed by {request.user.get_full_name()}',
                success=True
            )
            
            serializer = NightAuditSerializer(audit)
            return Response(serializer.data)
            
        except NightAudit.DoesNotExist:
            return Response(
                {'error': 'Night audit not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# ===== Audit Logs =====

class AuditLogListView(generics.ListAPIView):
    """List audit logs for a night audit."""
    permission_classes = [IsAuthenticated]
    serializer_class = AuditLogSerializer
    
    def get_queryset(self):
        audit_id = self.kwargs.get('audit_id')
        return AuditLog.objects.filter(
            night_audit_id=audit_id,
            night_audit__property=getattr(self.request.user, 'property', None)
        ).order_by('timestamp')


# ===== Dashboard & Stats =====

class NightAuditDashboardView(APIView):
    """Get night audit dashboard statistics."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db import models
        property_obj = request.user.property
        today = date.today()
        
        # Get last audit
        last_audit = NightAudit.objects.filter(
            property=property_obj
        ).order_by('-audit_date').first()
        
        # Statistics
        pending = NightAudit.objects.filter(
            property=property_obj,
            status='PENDING'
        ).count()
        
        # This month statistics
        completed_this_month = NightAudit.objects.filter(
            property=property_obj,
            status='COMPLETED',
            audit_date__year=today.year,
            audit_date__month=today.month
        )
        
        completed_count = completed_this_month.count()
        
        # Average duration
        avg_duration = 0
        if completed_count > 0:
            audits_with_duration = completed_this_month.filter(
                started_at__isnull=False,
                completed_at__isnull=False
            )
            if audits_with_duration.exists():
                total_seconds = sum([
                    (audit.completed_at - audit.started_at).total_seconds()
                    for audit in audits_with_duration
                ])
                avg_duration = round(total_seconds / audits_with_duration.count() / 60, 2)
        
        # Total revenue this month
        revenue = completed_this_month.aggregate(
            total=Sum('total_revenue')
        )['total'] or 0
        
        data = {
            'last_audit_date': last_audit.audit_date if last_audit else None,
            'last_audit_status': last_audit.status if last_audit else 'NONE',
            'pending_audits': pending,
            'completed_this_month': completed_count,
            'avg_duration_minutes': avg_duration,
            'total_revenue_this_month': revenue
        }
        
        serializer = NightAuditSummarySerializer(data)
        return Response(serializer.data)
