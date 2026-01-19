"""
API v1 URL Configuration
"""

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Authentication
    path('auth/', include('api.v1.auth.urls')),
    
    # Core modules
    path('properties/', include('api.v1.properties.urls')),
    path('rooms/', include('api.v1.rooms.urls')),
    path('reservations/', include('api.v1.reservations.urls')),
    path('guests/', include('api.v1.guests.urls')),
    
    # Operations
    path('frontdesk/', include('api.v1.frontdesk.urls')),
    path('housekeeping/', include('api.v1.housekeeping.urls')),
    path('maintenance/', include('api.v1.maintenance.urls')),
    
    # Financial
    path('billing/', include('api.v1.billing.urls')),
    path('pos/', include('api.v1.pos.urls')),
    
    # Revenue Management
    path('rates/', include('api.v1.rates.urls')),
    path('channels/', include('api.v1.channels.urls')),
    
    # Reports & Notifications
    path('reports/', include('api.v1.reports.urls')),
    path('notifications/', include('api.v1.notifications.urls')),
]
