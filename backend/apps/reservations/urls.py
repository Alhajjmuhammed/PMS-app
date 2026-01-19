from django.urls import path
from . import views

app_name = 'reservations'

urlpatterns = [
    # Reservations
    path('', views.ReservationListView.as_view(), name='reservation_list'),
    path('create/', views.ReservationCreateView.as_view(), name='reservation_create'),
    path('search/', views.ReservationSearchView.as_view(), name='reservation_search'),
    path('<int:pk>/', views.ReservationDetailView.as_view(), name='reservation_detail'),
    path('<int:pk>/edit/', views.ReservationUpdateView.as_view(), name='reservation_update'),
    path('<int:pk>/cancel/', views.ReservationCancelView.as_view(), name='reservation_cancel'),
    path('<int:pk>/confirm/', views.ReservationConfirmView.as_view(), name='reservation_confirm'),
    
    # Group Bookings
    path('groups/', views.GroupBookingListView.as_view(), name='group_list'),
    path('groups/create/', views.GroupBookingCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', views.GroupBookingDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/edit/', views.GroupBookingUpdateView.as_view(), name='group_update'),
    
    # Calendar View
    path('calendar/', views.ReservationCalendarView.as_view(), name='calendar'),
    
    # Availability
    path('availability/', views.AvailabilityView.as_view(), name='availability'),
]
