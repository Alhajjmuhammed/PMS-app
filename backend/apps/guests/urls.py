from django.urls import path
from . import views

app_name = 'guests'

urlpatterns = [
    # Guests
    path('', views.GuestListView.as_view(), name='guest_list'),
    path('create/', views.GuestCreateView.as_view(), name='guest_create'),
    path('search/', views.GuestSearchView.as_view(), name='guest_search'),
    path('<int:pk>/', views.GuestDetailView.as_view(), name='guest_detail'),
    path('<int:pk>/edit/', views.GuestUpdateView.as_view(), name='guest_update'),
    path('<int:pk>/history/', views.GuestHistoryView.as_view(), name='guest_history'),
    
    # Guest Preferences
    path('<int:guest_pk>/preferences/', views.GuestPreferenceListView.as_view(), name='preference_list'),
    path('<int:guest_pk>/preferences/add/', views.GuestPreferenceCreateView.as_view(), name='preference_create'),
    
    # Companies
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/create/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_update'),
    
    # Loyalty
    path('loyalty/', views.LoyaltyDashboardView.as_view(), name='loyalty_dashboard'),
    path('<int:guest_pk>/loyalty/transactions/', views.LoyaltyTransactionListView.as_view(), name='loyalty_transactions'),
]
