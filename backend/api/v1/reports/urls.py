from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard & Reports
    path('dashboard/', views.DashboardStatsView.as_view(), name='dashboard'),
    path('advanced-analytics/', views.AdvancedAnalyticsView.as_view(), name='advanced_analytics'),
    path('revenue-forecast/', views.RevenueForecastView.as_view(), name='revenue_forecast'),
    path('occupancy/', views.OccupancyReportView.as_view(), name='occupancy'),
    path('revenue/', views.RevenueReportView.as_view(), name='revenue'),
    path('daily/', views.DailyReportView.as_view(), name='daily'),
    
    # Monthly Statistics
    path('monthly-stats/', views.MonthlyStatisticsListCreateView.as_view(), name='monthly_stats_list'),
    path('monthly-stats/<int:pk>/', views.MonthlyStatisticsDetailView.as_view(), name='monthly_stats_detail'),
    
    # Night Audit
    path('night-audits/', views.NightAuditListCreateView.as_view(), name='night_audit_list'),
    path('night-audits/<int:pk>/', views.NightAuditDetailView.as_view(), name='night_audit_detail'),
    path('night-audits/<int:pk>/start/', views.StartNightAuditView.as_view(), name='night_audit_start'),
    path('night-audits/<int:pk>/complete/', views.CompleteNightAuditView.as_view(), name='night_audit_complete'),
    path('night-audits/<int:pk>/rollback/', views.RollbackNightAuditView.as_view(), name='night_audit_rollback'),
    path('night-audits/<int:night_audit_id>/logs/', views.AuditLogListView.as_view(), name='audit_logs'),
]
