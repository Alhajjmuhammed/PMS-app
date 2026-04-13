"""
Health check URL patterns
"""
from django.urls import path
from . import views

app_name = 'health'

urlpatterns = [
    # Basic health check endpoint
    path('', views.HealthCheckView.as_view(), name='health'),
    
    # Detailed health check with database status
    path('detailed/', views.DetailedHealthCheckView.as_view(), name='health_detailed'),
    
    # Container orchestration endpoints
    path('ready/', views.ReadinessCheckView.as_view(), name='readiness'),
    path('live/', views.LivenessCheckView.as_view(), name='liveness'),
]