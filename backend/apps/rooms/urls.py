from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    # Room Types
    path('types/', views.RoomTypeListView.as_view(), name='room_type_list'),
    path('types/create/', views.RoomTypeCreateView.as_view(), name='room_type_create'),
    path('types/<int:pk>/', views.RoomTypeDetailView.as_view(), name='room_type_detail'),
    path('types/<int:pk>/edit/', views.RoomTypeUpdateView.as_view(), name='room_type_update'),
    
    # Rooms
    path('', views.RoomListView.as_view(), name='room_list'),
    path('create/', views.RoomCreateView.as_view(), name='room_create'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room_update'),
    path('<int:pk>/status/', views.RoomStatusUpdateView.as_view(), name='room_status_update'),
    
    # Room Blocks
    path('blocks/', views.RoomBlockListView.as_view(), name='room_block_list'),
    path('blocks/create/', views.RoomBlockCreateView.as_view(), name='room_block_create'),
    
    # Room Grid (visual display)
    path('grid/', views.RoomGridView.as_view(), name='room_grid'),
    
    # Amenities
    path('amenities/', views.RoomAmenityListView.as_view(), name='amenity_list'),
]
