from django.urls import path
from . import views

app_name = 'housekeeping'

urlpatterns = [
    path('', views.HousekeepingDashboardView.as_view(), name='dashboard'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/update-status/', views.TaskStatusUpdateView.as_view(), name='task_status_update'),
    path('tasks/<int:pk>/assign/', views.TaskAssignView.as_view(), name='task_assign'),
    
    path('room-status/', views.RoomStatusBoardView.as_view(), name='room_status_board'),
    path('room/<int:room_pk>/update-status/', views.RoomStatusUpdateView.as_view(), name='room_status_update'),
    
    path('inspections/', views.InspectionListView.as_view(), name='inspection_list'),
    path('inspections/create/<int:room_pk>/', views.InspectionCreateView.as_view(), name='inspection_create'),
    
    path('inventory/linen/', views.LinenInventoryView.as_view(), name='linen_inventory'),
    path('inventory/amenities/', views.AmenityInventoryView.as_view(), name='amenity_inventory'),
    
    path('schedule/', views.ScheduleView.as_view(), name='schedule'),
]
