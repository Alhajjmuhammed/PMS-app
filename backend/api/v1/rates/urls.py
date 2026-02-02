from django.urls import path
from . import views
from . import rate_plan_views

app_name = 'rates'

urlpatterns = [
    # Rate Plans
    path('plans/', rate_plan_views.RatePlanListCreateView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', rate_plan_views.RatePlanDetailView.as_view(), name='plan_detail'),
    path('plans/active/', rate_plan_views.ActiveRatePlansView.as_view(), name='plan_active'),
    
    # Room Rates
    path('room-rates/', rate_plan_views.RoomRateListCreateView.as_view(), name='room_rate_list'),
    path('room-rates/<int:pk>/', rate_plan_views.RoomRateDetailView.as_view(), name='room_rate_detail'),
    path('room-rates/plan/<int:rate_plan_id>/', rate_plan_views.RoomRateByPlanView.as_view(), name='room_rate_by_plan'),
    path('room-rates/bulk/', rate_plan_views.BulkRoomRateCreateView.as_view(), name='room_rate_bulk'),
    
    # Date Rates (overrides)
    path('date-rates/', rate_plan_views.DateRateListCreateView.as_view(), name='date_rate_list'),
    path('date-rates/<int:pk>/', rate_plan_views.DateRateDetailView.as_view(), name='date_rate_detail'),
    path('date-rates/date/<str:date>/', rate_plan_views.DateRateByDateView.as_view(), name='date_rate_by_date'),
    
    # Yield Rules
    path('yield-rules/', rate_plan_views.YieldRuleListCreateView.as_view(), name='yield_rule_list'),
    path('yield-rules/<int:pk>/', rate_plan_views.YieldRuleDetailView.as_view(), name='yield_rule_detail'),
    path('yield-rules/active/', rate_plan_views.ActiveYieldRulesView.as_view(), name='yield_rule_active'),
    
    # Rate Calculation
    path('calculate/', rate_plan_views.CalculateRateView.as_view(), name='calculate_rate'),
    path('stats/', rate_plan_views.RateStatsView.as_view(), name='rate_stats'),
    
    # Seasons (existing)
    path('seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('seasons/<int:pk>/', views.SeasonDetailView.as_view(), name='season_detail'),
    
    # Packages (existing)
    path('packages/', views.PackageListCreateView.as_view(), name='package_list'),
    path('packages/<int:pk>/', views.PackageDetailView.as_view(), name='package_detail'),
    
    # Discounts (existing)
    path('discounts/', views.DiscountListCreateView.as_view(), name='discount_list'),
    path('discounts/<int:pk>/', views.DiscountDetailView.as_view(), name='discount_detail'),
]

