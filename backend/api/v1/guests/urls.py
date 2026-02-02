"""
URLs for Guests Enhanced API
"""
from django.urls import path
from . import views
from . import guests_views

app_name = 'guests'

urlpatterns = [
    # ===== Guest Preferences =====
    path('preferences/', guests_views.GuestPreferenceListCreateView.as_view(), name='preference_list'),
    path('preferences/<int:pk>/', guests_views.GuestPreferenceDetailView.as_view(), name='preference_detail'),
    path('<int:guest_id>/preferences/', guests_views.GuestPreferencesByGuestView.as_view(), name='guest_preferences'),
    
    # ===== Guest Documents =====
    path('documents/', guests_views.GuestDocumentListCreateView.as_view(), name='document_list'),
    path('documents/<int:pk>/', guests_views.GuestDocumentDetailView.as_view(), name='document_detail'),
    path('<int:guest_id>/documents/', guests_views.GuestDocumentsByGuestView.as_view(), name='guest_documents'),
    
    # ===== Companies =====
    path('companies/', guests_views.CompanyListCreateView.as_view(), name='company_list'),
    path('companies/<int:pk>/', guests_views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/active/', guests_views.ActiveCompaniesView.as_view(), name='active_companies'),
    
    # ===== Loyalty Programs =====
    path('loyalty/programs/', guests_views.LoyaltyProgramListCreateView.as_view(), name='loyalty_program_list'),
    path('loyalty/programs/<int:pk>/', guests_views.LoyaltyProgramDetailView.as_view(), name='loyalty_program_detail'),
    path('loyalty/programs/active/', guests_views.ActiveLoyaltyProgramsView.as_view(), name='active_loyalty_programs'),
    
    # ===== Loyalty Tiers =====
    path('loyalty/tiers/', guests_views.LoyaltyTierListCreateView.as_view(), name='loyalty_tier_list'),
    path('loyalty/tiers/<int:pk>/', guests_views.LoyaltyTierDetailView.as_view(), name='loyalty_tier_detail'),
    path('loyalty/programs/<int:program_id>/tiers/', guests_views.LoyaltyTiersByProgramView.as_view(), name='loyalty_tiers_by_program'),
    
    # ===== Loyalty Transactions =====
    path('loyalty/transactions/', guests_views.LoyaltyTransactionListCreateView.as_view(), name='loyalty_transaction_list'),
    path('loyalty/transactions/<int:pk>/', guests_views.LoyaltyTransactionDetailView.as_view(), name='loyalty_transaction_detail'),
    path('<int:guest_id>/loyalty/transactions/', guests_views.LoyaltyTransactionsByGuestView.as_view(), name='guest_loyalty_transactions'),
    
    # ===== Loyalty Actions =====
    path('<int:guest_id>/loyalty/earn/', guests_views.EarnLoyaltyPointsView.as_view(), name='earn_loyalty_points'),
    path('<int:guest_id>/loyalty/redeem/', guests_views.RedeemLoyaltyPointsView.as_view(), name='redeem_loyalty_points'),
    path('<int:guest_id>/loyalty/dashboard/', guests_views.GuestLoyaltyDashboardView.as_view(), name='guest_loyalty_dashboard'),
    
    # ===== Legacy compatibility =====
    path('', views.GuestListView.as_view(), name='list'),
    path('create/', views.GuestCreateView.as_view(), name='create'),
    path('<int:pk>/', views.GuestDetailView.as_view(), name='detail'),
    path('<int:guest_id>/documents/<int:document_id>/', views.GuestDocumentDetailView.as_view(), name='document_detail_legacy'),
    path('search/', views.GuestSearchView.as_view(), name='search'),
    path('<int:guest_id>/loyalty/balance/', views.GuestLoyaltyBalanceView.as_view(), name='guest_loyalty_balance'),
]

