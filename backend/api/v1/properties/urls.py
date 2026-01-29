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
]
