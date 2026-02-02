"""
URLs for Reports API
"""
from django.urls import path
from . import views
from . import reports_views

app_name = 'reports'

urlpatterns = [
    # ===== Daily Statistics =====
    path('daily-stats/', reports_views.DailyStatisticsListCreateView.as_view(), name='daily_stats_list'),
    path('daily-stats/<int:pk>/', reports_views.DailyStatisticsDetailView.as_view(), name='daily_stats_detail'),
    path('daily-stats/date/<str:date>/', reports_views.DailyStatisticsByDateView.as_view(), name='daily_stats_by_date'),
    
    # ===== Monthly Statistics =====
    path('monthly-stats/', reports_views.MonthlyStatisticsListCreateView.as_view(), name='monthly_stats_list'),
    path('monthly-stats/<int:pk>/', reports_views.MonthlyStatisticsDetailView.as_view(), name='monthly_stats_detail'),
    
    # ===== Report Templates =====
    path('templates/', reports_views.ReportTemplateListCreateView.as_view(), name='template_list'),
    path('templates/<int:pk>/', reports_views.ReportTemplateDetailView.as_view(), name='template_detail'),
    path('generate/', reports_views.GenerateReportView.as_view(), name='generate_report'),
    
    # ===== Night Audit =====
    path('night-audits/', reports_views.NightAuditListCreateView.as_view(), name='night_audit_list'),
    path('night-audits/<int:pk>/', reports_views.NightAuditDetailView.as_view(), name='night_audit_detail'),
    path('night-audits/pending/', reports_views.PendingNightAuditsView.as_view(), name='pending_night_audits'),
    path('night-audits/<int:pk>/start/', reports_views.StartNightAuditView.as_view(), name='night_audit_start'),
    path('night-audits/<int:pk>/complete/', reports_views.CompleteNightAuditView.as_view(), name='night_audit_complete'),
    path('night-audits/<int:audit_id>/logs/', reports_views.AuditLogListView.as_view(), name='audit_logs'),
    path('night-audits/dashboard/', reports_views.NightAuditDashboardView.as_view(), name='night_audit_dashboard'),
    
    # ===== Legacy compatibility =====
    path('dashboard/', views.DashboardStatsView.as_view(), name='dashboard'),
    path('advanced-analytics/', views.AdvancedAnalyticsView.as_view(), name='advanced_analytics'),
    path('revenue-forecast/', views.RevenueForecastView.as_view(), name='revenue_forecast'),
    path('occupancy/', views.OccupancyReportView.as_view(), name='occupancy'),
    path('revenue/', views.RevenueReportView.as_view(), name='revenue'),
    path('daily/', views.DailyReportView.as_view(), name='daily'),
    path('night-audits/<int:pk>/rollback/', views.RollbackNightAuditView.as_view(), name='night_audit_rollback'),
]
