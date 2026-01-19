from django.urls import path
from . import views

app_name = 'rates'

urlpatterns = [
    path('', views.RateDashboardView.as_view(), name='dashboard'),
    path('plans/', views.RatePlanListView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.RatePlanDetailView.as_view(), name='plan_detail'),
    path('plans/<int:pk>/edit/', views.RatePlanEditView.as_view(), name='plan_edit'),
    path('seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('packages/', views.PackageListView.as_view(), name='package_list'),
    path('discounts/', views.DiscountListView.as_view(), name='discount_list'),
    path('calendar/', views.RateCalendarView.as_view(), name='calendar'),
    path('yield-rules/', views.YieldRuleListView.as_view(), name='yield_rules'),
]
