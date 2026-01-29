from django.urls import path
from . import views

app_name = 'rates'

urlpatterns = [
    # Rate Plan endpoints
    path('plans/', views.RatePlanListView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.RatePlanDetailView.as_view(), name='plan_detail'),
    
    # Season endpoints
    path('seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('seasons/<int:pk>/', views.SeasonDetailView.as_view(), name='season_detail'),
    
    # Room Rate endpoints
    path('room-rates/', views.RoomRateListCreateView.as_view(), name='room_rate_list'),
    path('room-rates/<int:pk>/', views.RoomRateDetailView.as_view(), name='room_rate_detail'),
    
    # Date Rate endpoints (overrides)
    path('date-rates/', views.DateRateListCreateView.as_view(), name='date_rate_list'),
    path('date-rates/<int:pk>/', views.DateRateDetailView.as_view(), name='date_rate_detail'),
]
