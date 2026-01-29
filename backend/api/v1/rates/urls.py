from django.urls import path
from . import views

app_name = 'rates'

urlpatterns = [
    path('plans/', views.RatePlanListView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.RatePlanDetailView.as_view(), name='plan_detail'),
    path('seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('seasons/<int:pk>/', views.SeasonDetailView.as_view(), name='season_detail'),
    path('room-rates/', views.RoomRateListView.as_view(), name='room_rate_list'),
]
