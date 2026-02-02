from django.urls import path
from . import views
from . import guest_message_views
from . import checkin_views

app_name = 'frontdesk'

urlpatterns = [
    # Legacy dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # New Check-In/Check-Out CRUD
    path('check-ins/', checkin_views.CheckInListCreateView.as_view(), name='checkin_list'),
    path('check-ins/<int:pk>/', checkin_views.CheckInDetailView.as_view(), name='checkin_detail'),
    path('check-ins/today/', checkin_views.TodayCheckInsView.as_view(), name='checkin_today'),
    
    path('check-outs/', checkin_views.CheckOutListCreateView.as_view(), name='checkout_list'),
    path('check-outs/<int:pk>/', checkin_views.CheckOutDetailView.as_view(), name='checkout_detail'),
    path('check-outs/today/', checkin_views.TodayCheckOutsView.as_view(), name='checkout_today'),
    
    # Room Moves
    path('room-moves/', checkin_views.RoomMoveListCreateView.as_view(), name='room_move_list'),
    path('room-moves/<int:pk>/', checkin_views.RoomMoveDetailView.as_view(), name='room_move_detail'),
    
    # Walk-Ins
    path('walk-ins/', checkin_views.WalkInListCreateView.as_view(), name='walk_in_list'),
    path('walk-ins/<int:pk>/', checkin_views.WalkInDetailView.as_view(), name='walk_in_detail'),
    path('walk-ins/<int:pk>/convert/', checkin_views.ConvertWalkInView.as_view(), name='walk_in_convert'),
    
    # Front Desk Dashboard
    path('dashboard-stats/', checkin_views.FrontDeskDashboardView.as_view(), name='dashboard_stats'),
    
    # Legacy endpoints (keep for backward compatibility)
    path('check-in/', views.CheckInView.as_view(), name='check_in'),
    path('check-in/<int:pk>/', views.CheckInWithIDView.as_view(), name='check_in_with_id'),
    path('check-out/', views.CheckOutView.as_view(), name='check_out'),
    path('check-out/<int:pk>/', views.CheckOutWithIDView.as_view(), name='check_out_with_id'),
    path('arrivals/', views.ArrivalsView.as_view(), name='arrivals'),
    path('departures/', views.DeparturesView.as_view(), name='departures'),
    path('in-house/', views.InHouseView.as_view(), name='in_house'),
    path('room-move/', views.RoomMoveView.as_view(), name='room_move'),
    
    # Guest Messages
    path('messages/', guest_message_views.GuestMessageListCreateView.as_view(), name='message_list'),
    path('messages/<int:pk>/', guest_message_views.GuestMessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/deliver/', guest_message_views.MarkMessageDeliveredView.as_view(), name='message_deliver'),
    path('messages/undelivered/', guest_message_views.UndeliveredMessagesView.as_view(), name='message_undelivered'),
    path('messages/check-in/<int:check_in_id>/', guest_message_views.MessagesByCheckInView.as_view(), name='message_by_checkin'),
    path('messages/room/<int:room_id>/', guest_message_views.MessagesByRoomView.as_view(), name='message_by_room'),
    path('messages/stats/', guest_message_views.GuestMessageStatsView.as_view(), name='message_stats'),
]

