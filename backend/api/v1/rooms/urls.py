from django.urls import path
from . import views
from . import room_block_views
from . import room_config_views

app_name = 'rooms'

urlpatterns = [
    # Room endpoints
    path('', views.RoomListView.as_view(), name='list'),
    path('create/', views.RoomCreateView.as_view(), name='create'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='detail'),
    path('<int:pk>/status/', views.UpdateRoomStatusView.as_view(), name='update_status'),
    
    # Room Images (legacy paths)
    path('<int:room_id>/images/', views.RoomImageListView.as_view(), name='image_list'),
    path('<int:room_id>/images/<int:image_id>/', views.RoomImageDetailView.as_view(), name='image_detail'),
    
    # Room Types - Full CRUD
    path('types/', room_config_views.RoomTypeListCreateView.as_view(), name='type_list'),
    path('types/<int:pk>/', room_config_views.RoomTypeDetailView.as_view(), name='type_detail'),
    path('types/active/', room_config_views.ActiveRoomTypesView.as_view(), name='type_active'),
    
    # Room Amenities - Full CRUD
    path('amenities/', room_config_views.RoomAmenityListCreateView.as_view(), name='amenity_list'),
    path('amenities/<int:pk>/', room_config_views.RoomAmenityDetailView.as_view(), name='amenity_detail'),
    path('amenities/active/', room_config_views.ActiveRoomAmenitiesView.as_view(), name='amenity_active'),
    
    # Room Type Amenities - Assignments
    path('type-amenities/', room_config_views.RoomTypeAmenityListCreateView.as_view(), name='type_amenity_list'),
    path('type-amenities/<int:pk>/', room_config_views.RoomTypeAmenityDetailView.as_view(), name='type_amenity_detail'),
    path('type-amenities/room-type/<int:room_type_id>/', room_config_views.RoomTypeAmenitiesByTypeView.as_view(), name='type_amenity_by_type'),
    path('type-amenities/bulk/', room_config_views.BulkAmenityAssignView.as_view(), name='type_amenity_bulk'),
    
    # Room Images - Full CRUD
    path('images/', room_config_views.RoomImageListCreateView.as_view(), name='images_list'),
    path('images/<int:pk>/', room_config_views.RoomImageDetailView.as_view(), name='images_detail'),
    path('images/room/<int:room_id>/', room_config_views.RoomImagesByRoomView.as_view(), name='images_by_room'),
    
    # Room Status Logs
    path('status-logs/', room_config_views.RoomStatusLogListCreateView.as_view(), name='status_log_list'),
    path('status-logs/<int:pk>/', room_config_views.RoomStatusLogDetailView.as_view(), name='status_log_detail'),
    path('status-logs/room/<int:room_id>/', room_config_views.RoomStatusLogsByRoomView.as_view(), name='status_log_by_room'),
    
    # Statistics
    path('config-stats/', room_config_views.RoomConfigStatsView.as_view(), name='config_stats'),
    
    # Room Blocks
    path('blocks/', room_block_views.RoomBlockListCreateView.as_view(), name='block_list'),
    path('blocks/<int:pk>/', room_block_views.RoomBlockDetailView.as_view(), name='block_detail'),
    path('blocks/by-date/', room_block_views.RoomBlocksByDateView.as_view(), name='block_by_date'),
    path('blocks/active/', room_block_views.ActiveRoomBlocksView.as_view(), name='block_active'),
    path('blocks/stats/', room_block_views.RoomBlockStatsView.as_view(), name='block_stats'),
    
    # Availability endpoints (legacy)
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('available/', views.AvailableRoomsView.as_view(), name='available'),
]

