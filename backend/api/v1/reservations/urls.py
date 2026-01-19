from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
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
]
