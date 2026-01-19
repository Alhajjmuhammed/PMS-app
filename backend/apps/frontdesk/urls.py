from django.urls import path
from . import views

app_name = 'frontdesk'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Arrivals & Departures
    path('arrivals/', views.ArrivalsView.as_view(), name='arrivals'),
    path('departures/', views.DeparturesView.as_view(), name='departures'),
    path('in-house/', views.InHouseView.as_view(), name='in_house'),
    
    # Check-in
    path('check-in/<int:reservation_pk>/', views.CheckInView.as_view(), name='check_in'),
    path('check-in/walk-in/', views.WalkInCheckInView.as_view(), name='walk_in_check_in'),
    
    # Check-out
    path('check-out/<int:check_in_pk>/', views.CheckOutView.as_view(), name='check_out'),
    path('check-out/express/<int:check_in_pk>/', views.ExpressCheckOutView.as_view(), name='express_check_out'),
    
    # Room Operations
    path('room-move/<int:check_in_pk>/', views.RoomMoveView.as_view(), name='room_move'),
    path('room-assignment/', views.RoomAssignmentView.as_view(), name='room_assignment'),
    
    # Walk-ins
    path('walk-ins/', views.WalkInListView.as_view(), name='walk_in_list'),
    path('walk-ins/create/', views.WalkInCreateView.as_view(), name='walk_in_create'),
    
    # Guest Messages
    path('messages/', views.GuestMessageListView.as_view(), name='message_list'),
    path('messages/create/<int:check_in_pk>/', views.GuestMessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/deliver/', views.GuestMessageDeliverView.as_view(), name='message_deliver'),
    
    # Room Grid
    path('room-grid/', views.RoomGridView.as_view(), name='room_grid'),
]
