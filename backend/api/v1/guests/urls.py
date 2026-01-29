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
]
