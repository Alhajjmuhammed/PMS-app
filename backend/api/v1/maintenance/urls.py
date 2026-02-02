"""
URLs for Maintenance API
"""
from django.urls import path
from . import views
from . import maintenance_views

app_name = 'maintenance'

urlpatterns = [
    # ===== Maintenance Requests =====
    path('requests/', maintenance_views.MaintenanceRequestListCreateView.as_view(), name='request_list'),
    path('requests/<int:pk>/', maintenance_views.MaintenanceRequestDetailView.as_view(), name='request_detail'),
    path('requests/pending/', maintenance_views.PendingMaintenanceView.as_view(), name='pending_requests'),
    path('requests/my-tasks/', maintenance_views.MyMaintenanceTasksView.as_view(), name='my_tasks'),
    path('requests/emergency/', maintenance_views.EmergencyMaintenanceView.as_view(), name='emergency_requests'),
    path('requests/<int:pk>/assign/', maintenance_views.AssignMaintenanceView.as_view(), name='assign_request'),
    path('requests/bulk-assign/', maintenance_views.BulkAssignMaintenanceView.as_view(), name='bulk_assign'),
    path('requests/<int:pk>/start/', maintenance_views.StartMaintenanceView.as_view(), name='start_request'),
    path('requests/<int:pk>/complete/', maintenance_views.CompleteMaintenanceView.as_view(), name='complete_request'),
    
    # ===== Assets =====
    path('assets/', maintenance_views.AssetListCreateView.as_view(), name='asset_list'),
    path('assets/<int:pk>/', maintenance_views.AssetDetailView.as_view(), name='asset_detail'),
    path('assets/room/<int:room_id>/', maintenance_views.AssetsByRoomView.as_view(), name='assets_by_room'),
    path('assets/due-maintenance/', maintenance_views.AssetsDueMaintenanceView.as_view(), name='assets_due_maintenance'),
    
    # ===== Maintenance Logs =====
    path('requests/<int:request_id>/logs/', maintenance_views.MaintenanceLogListView.as_view(), name='log_list'),
    path('logs/', maintenance_views.MaintenanceLogCreateView.as_view(), name='log_create'),
    
    # ===== Dashboard =====
    path('dashboard/', maintenance_views.MaintenanceDashboardView.as_view(), name='dashboard'),
    
    # ===== Legacy compatibility =====
    path('', views.RequestListView.as_view(), name='request_list_legacy'),
    path('<int:pk>/', views.RequestDetailView.as_view(), name='request_detail_api'),
    path('<int:pk>/start/', views.StartRequestView.as_view(), name='start'),
    path('<int:pk>/complete/', views.CompleteRequestView.as_view(), name='complete'),
    path('<int:pk>/resolve/', views.ResolveRequestView.as_view(), name='resolve'),
    path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/assign/', views.AssignRequestView.as_view(), name='assign'),
    path('my-requests/', views.MyRequestsView.as_view(), name='my_requests'),
]
