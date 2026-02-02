"""
URLs for Channels API
"""
from django.urls import path
from . import views
from . import channels_views

app_name = 'channels'

urlpatterns = [
    # ===== Global Channels =====
    path('available/', channels_views.ChannelListView.as_view(), name='available_channels'),
    
    # ===== Property Channels =====
    path('property-channels/', channels_views.PropertyChannelListCreateView.as_view(), name='property_channel_list'),
    path('property-channels/<int:pk>/', channels_views.PropertyChannelDetailView.as_view(), name='property_channel_detail'),
    path('property-channels/active/', channels_views.ActivePropertyChannelsView.as_view(), name='active_property_channels'),
    path('property-channels/<int:pk>/sync/', channels_views.SyncPropertyChannelView.as_view(), name='sync_property_channel'),
    
    # ===== Room Type Mappings =====
    path('room-mappings/', channels_views.RoomTypeMappingListCreateView.as_view(), name='room_mapping_list'),
    path('room-mappings/<int:pk>/', channels_views.RoomTypeMappingDetailView.as_view(), name='room_mapping_detail'),
    path('room-mappings/channel/<int:channel_id>/', channels_views.RoomTypeMappingsByChannelView.as_view(), name='room_mappings_by_channel'),
    
    # ===== Rate Plan Mappings =====
    path('rate-mappings/', channels_views.RatePlanMappingListCreateView.as_view(), name='rate_mapping_list'),
    path('rate-mappings/<int:pk>/', channels_views.RatePlanMappingDetailView.as_view(), name='rate_mapping_detail'),
    path('rate-mappings/channel/<int:channel_id>/', channels_views.RatePlanMappingsByChannelView.as_view(), name='rate_mappings_by_channel'),
    
    # ===== Availability Updates =====
    path('availability-updates/', channels_views.AvailabilityUpdateListCreateView.as_view(), name='availability_update_list'),
    path('availability-updates/<int:pk>/', channels_views.AvailabilityUpdateDetailView.as_view(), name='availability_update_detail'),
    path('availability-updates/bulk/', channels_views.BulkAvailabilityUpdateView.as_view(), name='bulk_availability_update'),
    
    # ===== Rate Updates =====
    path('rate-updates/', channels_views.RateUpdateListCreateView.as_view(), name='rate_update_list'),
    path('rate-updates/<int:pk>/', channels_views.RateUpdateDetailView.as_view(), name='rate_update_detail'),
    path('rate-updates/bulk/', channels_views.BulkRateUpdateView.as_view(), name='bulk_rate_update'),
    
    # ===== Channel Reservations =====
    path('reservations/', channels_views.ChannelReservationListView.as_view(), name='reservation_list'),
    path('reservations/<int:pk>/', channels_views.ChannelReservationDetailView.as_view(), name='reservation_detail'),
    path('reservations/unprocessed/', channels_views.UnprocessedChannelReservationsView.as_view(), name='unprocessed_reservations'),
    
    # ===== Dashboard =====
    path('dashboard/', channels_views.ChannelDashboardView.as_view(), name='dashboard'),
    
    # ===== Legacy compatibility =====
    path('', views.ChannelListView.as_view(), name='channel_list'),
    path('<int:pk>/', views.ChannelDetailView.as_view(), name='channel_detail'),
]
