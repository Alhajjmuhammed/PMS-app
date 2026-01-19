from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.DashboardStatsView.as_view(), name='dashboard'),
    path('advanced-analytics/', views.AdvancedAnalyticsView.as_view(), name='advanced_analytics'),
    path('revenue-forecast/', views.RevenueForecastView.as_view(), name='revenue_forecast'),
    path('occupancy/', views.OccupancyReportView.as_view(), name='occupancy'),
    path('revenue/', views.RevenueReportView.as_view(), name='revenue'),
    path('daily/', views.DailyReportView.as_view(), name='daily'),
]
