from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),
    
    # Standard reports
    path('daily/', views.DailyReportView.as_view(), name='daily'),
    path('occupancy/', views.OccupancyReportView.as_view(), name='occupancy'),
    path('revenue/', views.RevenueReportView.as_view(), name='revenue'),
    path('arrivals/', views.ArrivalsReportView.as_view(), name='arrivals'),
    path('departures/', views.DeparturesReportView.as_view(), name='departures'),
    path('in-house/', views.InHouseReportView.as_view(), name='in_house'),
    path('production/', views.ProductionReportView.as_view(), name='production'),
    path('forecast/', views.ForecastReportView.as_view(), name='forecast'),
    
    # Night audit
    path('night-audit/', views.NightAuditView.as_view(), name='night_audit'),
    path('night-audit/<int:pk>/', views.NightAuditDetailView.as_view(), name='night_audit_detail'),
    path('night-audit/run/', views.RunNightAuditView.as_view(), name='run_night_audit'),
    
    # Statistics
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    
    # Custom reports
    path('templates/', views.ReportTemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/run/', views.RunReportView.as_view(), name='run_report'),
]
