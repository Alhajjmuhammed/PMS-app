from django.urls import path
from . import views

app_name = 'frontdesk'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('check-in/', views.CheckInView.as_view(), name='check_in'),
    path('check-in/<int:pk>/', views.CheckInWithIDView.as_view(), name='check_in_with_id'),
    path('check-out/', views.CheckOutView.as_view(), name='check_out'),
    path('check-out/<int:pk>/', views.CheckOutWithIDView.as_view(), name='check_out_with_id'),
    path('arrivals/', views.ArrivalsView.as_view(), name='arrivals'),
    path('departures/', views.DeparturesView.as_view(), name='departures'),
    path('in-house/', views.InHouseView.as_view(), name='in_house'),
    path('room-move/', views.RoomMoveView.as_view(), name='room_move'),
    
    # Walk-Ins
    path('walk-ins/', views.WalkInListCreateView.as_view(), name='walk_in_list'),
    path('walk-ins/<int:pk>/', views.WalkInDetailView.as_view(), name='walk_in_detail'),
    path('walk-ins/<int:pk>/convert/', views.ConvertWalkInView.as_view(), name='walk_in_convert'),
]
