from django.urls import path
from . import views

app_name = 'channels'

urlpatterns = [
    path('', views.ChannelDashboardView.as_view(), name='dashboard'),
    path('list/', views.ChannelListView.as_view(), name='channel_list'),
    path('<int:pk>/', views.ChannelDetailView.as_view(), name='channel_detail'),
    path('connections/', views.ConnectionListView.as_view(), name='connection_list'),
    path('connections/<int:pk>/', views.ConnectionDetailView.as_view(), name='connection_detail'),
    path('connections/<int:pk>/sync/', views.SyncChannelView.as_view(), name='sync'),
    path('reservations/', views.ChannelReservationListView.as_view(), name='reservation_list'),
    path('updates/', views.UpdateLogView.as_view(), name='update_log'),
]
