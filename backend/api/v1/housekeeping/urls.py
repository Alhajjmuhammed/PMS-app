from django.urls import path
from . import views
from . import housekeeping_views

app_name = 'housekeeping'

urlpatterns = [
    # ===== Housekeeping Tasks =====
    path('tasks/', housekeeping_views.HousekeepingTaskListCreateView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', housekeeping_views.HousekeepingTaskDetailView.as_view(), name='task_detail'),
    path('tasks/today/', housekeeping_views.TodayTasksView.as_view(), name='tasks_today'),
    path('tasks/my-tasks/', housekeeping_views.MyTasksView.as_view(), name='my_tasks'),
    path('tasks/<int:pk>/start/', housekeeping_views.StartTaskView.as_view(), name='start_task'),
    path('tasks/<int:pk>/complete/', housekeeping_views.CompleteTaskView.as_view(), name='complete_task'),
    path('tasks/bulk-assign/', housekeeping_views.BulkTaskAssignView.as_view(), name='bulk_assign_tasks'),
    
    # ===== Room Inspections =====
    path('inspections/', housekeeping_views.RoomInspectionListCreateView.as_view(), name='inspection_list'),
    path('inspections/<int:pk>/', housekeeping_views.RoomInspectionDetailView.as_view(), name='inspection_detail'),
    path('inspections/room/<int:room_id>/', housekeeping_views.InspectionsByRoomView.as_view(), name='inspections_by_room'),
    
    # ===== Linen Inventory =====
    path('inventory/linens/', housekeeping_views.LinenInventoryListCreateView.as_view(), name='linen_inventory_list'),
    path('inventory/linens/<int:pk>/', housekeeping_views.LinenInventoryDetailView.as_view(), name='linen_inventory_detail'),
    path('inventory/linens/low-stock/', housekeeping_views.LowLinenStockView.as_view(), name='low_linen_stock'),
    
    # ===== Amenity Inventory =====
    path('inventory/amenities/', housekeeping_views.AmenityInventoryListCreateView.as_view(), name='amenity_inventory_list'),
    path('inventory/amenities/<int:pk>/', housekeeping_views.AmenityInventoryDetailView.as_view(), name='amenity_inventory_detail'),
    path('inventory/amenities/low-stock/', housekeeping_views.LowAmenityStockView.as_view(), name='low_amenity_stock'),
    
    # ===== Stock Movements =====
    path('inventory/movements/', housekeeping_views.StockMovementListCreateView.as_view(), name='stock_movement_list'),
    path('inventory/movements/<int:pk>/', housekeeping_views.StockMovementDetailView.as_view(), name='stock_movement_detail'),
    
    # ===== Housekeeping Schedules =====
    path('schedules/', housekeeping_views.HousekeepingScheduleListCreateView.as_view(), name='schedule_list'),
    path('schedules/<int:pk>/', housekeeping_views.HousekeepingScheduleDetailView.as_view(), name='schedule_detail'),
    
    # ===== Dashboard =====
    path('dashboard/', housekeeping_views.HousekeepingDashboardView.as_view(), name='dashboard'),
]

