from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    # Room endpoints
    path('', views.RoomListView.as_view(), name='list'),
    path('create/', views.RoomCreateView.as_view(), name='create'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='detail'),
    path('<int:pk>/status/', views.UpdateRoomStatusView.as_view(), name='update_status'),
    path('<int:room_id>/images/', views.RoomImageListView.as_view(), name='image_list'),
    path('<int:room_id>/images/<int:image_id>/', views.RoomImageDetailView.as_view(), name='image_detail'),
    
    # Room Type endpoints
    path('types/', views.RoomTypeListView.as_view(), name='type_list'),
    path('types/<int:pk>/', views.RoomTypeDetailView.as_view(), name='type_detail'),
    
    # Room Amenity endpoints
    path('amenities/', views.RoomAmenityListCreateView.as_view(), name='amenity_list'),
    path('amenities/<int:pk>/', views.RoomAmenityDetailView.as_view(), name='amenity_detail'),
    
    # Room Type Amenity assignments
    path('types/<int:room_type_id>/amenities/', views.RoomTypeAmenityListCreateView.as_view(), name='type_amenity_list'),
    path('types/<int:room_type_id>/amenities/<int:amenity_assignment_id>/', views.RoomTypeAmenityDetailView.as_view(), name='type_amenity_detail'),
    
    # Availability endpoints
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('available/', views.AvailableRoomsView.as_view(), name='available'),
]
