from django.urls import path
from . import views

app_name = 'channels'

urlpatterns = [
    path('', views.ChannelListView.as_view(), name='channel_list'),
    path('<int:pk>/', views.ChannelDetailView.as_view(), name='channel_detail'),
    path('property-channels/', views.PropertyChannelListView.as_view(), name='property_channel_list'),
    path('property-channels/<int:pk>/', views.PropertyChannelDetailView.as_view(), name='property_channel_detail'),
    path('room-mappings/', views.RoomTypeMappingListView.as_view(), name='room_mapping_list'),
]
