from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Property endpoints
    path('', views.PropertyListView.as_view(), name='list'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='detail'),
    path('settings/', views.SystemSettingView.as_view(), name='settings'),
    
    # Building endpoints
    path('buildings/', views.BuildingListCreateView.as_view(), name='building_list'),
    path('buildings/<int:pk>/', views.BuildingDetailView.as_view(), name='building_detail'),
    
    # Floor endpoints
    path('floors/', views.FloorListCreateView.as_view(), name='floor_list'),
    path('floors/<int:pk>/', views.FloorDetailView.as_view(), name='floor_detail'),
    
    # Department endpoints
    path('departments/', views.DepartmentListCreateView.as_view(), name='department_list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/<int:pk>/staff/', views.DepartmentStaffView.as_view(), name='department_staff'),
    
    # Property Amenity endpoints
    path('amenities/', views.PropertyAmenityListCreateView.as_view(), name='amenity_list'),
    path('amenities/<int:pk>/', views.PropertyAmenityDetailView.as_view(), name='amenity_detail'),
    
    # Tax Configuration endpoints
    path('taxes/', views.TaxConfigurationListCreateView.as_view(), name='tax_list'),
    path('taxes/<int:pk>/', views.TaxConfigurationDetailView.as_view(), name='tax_detail'),
    path('taxes/active/', views.ActiveTaxesView.as_view(), name='tax_active'),
]

