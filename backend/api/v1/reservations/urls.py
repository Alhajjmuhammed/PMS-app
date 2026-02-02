from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # Reservations
    path('', views.ReservationListView.as_view(), name='list'),
    path('create/', views.ReservationCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReservationDetailView.as_view(), name='detail'),
    path('<int:pk>/cancel/', views.CancelReservationView.as_view(), name='cancel'),
    path('arrivals/', views.ArrivalsView.as_view(), name='arrivals'),
    path('departures/', views.DeparturesView.as_view(), name='departures'),
    
    # Availability
    path('check-availability/', views.CheckAvailabilityView.as_view(), name='check_availability'),
    path('availability-calendar/', views.AvailabilityCalendarView.as_view(), name='availability_calendar'),
    
    # Pricing
    path('calculate-price/', views.CalculatePriceView.as_view(), name='calculate_price'),
    path('compare-rates/', views.CompareRatesView.as_view(), name='compare_rates'),
    
    # Group Bookings
    path('groups/', views.GroupBookingListCreateView.as_view(), name='group_list'),
    path('groups/<int:pk>/', views.GroupBookingDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/pickup/', views.GroupBookingRoomPickupView.as_view(), name='group_pickup'),
    path('groups/<int:pk>/confirm/', views.GroupBookingConfirmView.as_view(), name='group_confirm'),
    path('groups/<int:pk>/cancel/', views.GroupBookingCancelView.as_view(), name='group_cancel'),
]
