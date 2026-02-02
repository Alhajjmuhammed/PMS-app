from django.urls import path
from . import views

app_name = 'guests'

urlpatterns = [
    # Guest endpoints
    path('', views.GuestListView.as_view(), name='list'),
    path('create/', views.GuestCreateView.as_view(), name='create'),
    path('<int:pk>/', views.GuestDetailView.as_view(), name='detail'),
    path('<int:guest_id>/documents/', views.GuestDocumentListView.as_view(), name='document_list'),
    path('<int:guest_id>/documents/<int:document_id>/', views.GuestDocumentDetailView.as_view(), name='document_detail'),
    path('search/', views.GuestSearchView.as_view(), name='search'),
    
    # Company endpoints
    path('companies/', views.CompanyListCreateView.as_view(), name='company_list'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    
    # Loyalty Program endpoints
    path('loyalty/programs/', views.LoyaltyProgramListCreateView.as_view(), name='loyalty_program_list'),
    path('loyalty/programs/<int:pk>/', views.LoyaltyProgramDetailView.as_view(), name='loyalty_program_detail'),
    path('loyalty/tiers/', views.LoyaltyTierListCreateView.as_view(), name='loyalty_tier_list'),
    path('loyalty/tiers/<int:pk>/', views.LoyaltyTierDetailView.as_view(), name='loyalty_tier_detail'),
    path('loyalty/transactions/', views.LoyaltyTransactionListCreateView.as_view(), name='loyalty_transaction_list'),
    path('loyalty/transactions/<int:pk>/', views.LoyaltyTransactionDetailView.as_view(), name='loyalty_transaction_detail'),
    path('<int:guest_id>/loyalty/balance/', views.GuestLoyaltyBalanceView.as_view(), name='guest_loyalty_balance'),
]
