from django.urls import path
from . import views

app_name = 'channels'

urlpatterns = [
    # Channels
    path('', views.ChannelListView.as_view(), name='channel_list'),
    path('<int:pk>/', views.ChannelDetailView.as_view(), name='channel_detail'),
    
    # Property Channels
    path('property-channels/', views.PropertyChannelListView.as_view(), name='property_channel_list'),
    path('property-channels/<int:pk>/', views.PropertyChannelDetailView.as_view(), name='property_channel_detail'),
    
    # Room Type Mappings
    path('room-mappings/', views.RoomTypeMappingListView.as_view(), name='room_mapping_list'),
    
    # Rate Plan Mappings
    path('rate-mappings/', views.RatePlanMappingListCreateView.as_view(), name='rate_mapping_list'),
    path('rate-mappings/<int:pk>/', views.RatePlanMappingDetailView.as_view(), name='rate_mapping_detail'),
    
    # Availability Updates
    path('availability-updates/', views.AvailabilityUpdateListCreateView.as_view(), name='availability_update_list'),
    path('availability-updates/<int:pk>/', views.AvailabilityUpdateDetailView.as_view(), name='availability_update_detail'),
    path('availability-updates/<int:pk>/resend/', views.ResendAvailabilityUpdateView.as_view(), name='availability_update_resend'),
    
    # Rate Updates
    path('rate-updates/', views.RateUpdateListCreateView.as_view(), name='rate_update_list'),
    path('rate-updates/<int:pk>/', views.RateUpdateDetailView.as_view(), name='rate_update_detail'),
    path('rate-updates/<int:pk>/resend/', views.ResendRateUpdateView.as_view(), name='rate_update_resend'),
    
    # Channel Reservations
    path('reservations/', views.ChannelReservationListCreateView.as_view(), name='reservation_list'),
    path('reservations/<int:pk>/', views.ChannelReservationDetailView.as_view(), name='reservation_detail'),
    path('reservations/<int:pk>/process/', views.ProcessChannelReservationView.as_view(), name='reservation_process'),
    path('reservations/<int:pk>/cancel/', views.CancelChannelReservationView.as_view(), name='reservation_cancel'),
]
