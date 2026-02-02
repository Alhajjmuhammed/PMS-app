from django.urls import path
from . import views

app_name = 'housekeeping'

urlpatterns = [
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/start/', views.StartTaskView.as_view(), name='start_task'),
    path('tasks/<int:pk>/complete/', views.CompleteTaskView.as_view(), name='complete_task'),
    path('my-tasks/', views.MyTasksView.as_view(), name='my_tasks'),
    path('rooms/', views.RoomStatusView.as_view(), name='room_status'),
    path('rooms/<int:pk>/status/', views.UpdateRoomStatusView.as_view(), name='update_room_status'),
    
    # Inventory Management
    path('inventory/amenities/', views.AmenityInventoryListCreateView.as_view(), name='amenity_inventory_list'),
    path('inventory/amenities/<int:pk>/', views.AmenityInventoryDetailView.as_view(), name='amenity_inventory_detail'),
    path('inventory/linens/', views.LinenInventoryListCreateView.as_view(), name='linen_inventory_list'),
    path('inventory/linens/<int:pk>/', views.LinenInventoryDetailView.as_view(), name='linen_inventory_detail'),
    path('inventory/movements/', views.StockMovementListCreateView.as_view(), name='stock_movement_list'),
    path('inventory/movements/<int:pk>/', views.StockMovementDetailView.as_view(), name='stock_movement_detail'),
]

