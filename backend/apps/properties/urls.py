from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.PropertyListView.as_view(), name='property_list'),
    path('create/', views.PropertyCreateView.as_view(), name='property_create'),
    path('<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_update'),
    path('<int:pk>/delete/', views.PropertyDeleteView.as_view(), name='property_delete'),
    
    # Buildings
    path('<int:property_pk>/buildings/', views.BuildingListView.as_view(), name='building_list'),
    path('<int:property_pk>/buildings/create/', views.BuildingCreateView.as_view(), name='building_create'),
    
    # Departments
    path('<int:property_pk>/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('<int:property_pk>/departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
]
