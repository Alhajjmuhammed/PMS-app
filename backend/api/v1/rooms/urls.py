from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.RoomListView.as_view(), name='list'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='detail'),
    path('<int:pk>/status/', views.UpdateRoomStatusView.as_view(), name='update_status'),
    path('<int:room_id>/images/', views.RoomImageListView.as_view(), name='image_list'),
    path('<int:room_id>/images/<int:image_id>/', views.RoomImageDetailView.as_view(), name='image_detail'),
    path('types/', views.RoomTypeListView.as_view(), name='type_list'),
    path('types/<int:pk>/', views.RoomTypeDetailView.as_view(), name='type_detail'),
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
    path('available/', views.AvailableRoomsView.as_view(), name='available'),
]
