from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.RequestListView.as_view(), name='request_list'),
    path('<int:pk>/', views.RequestDetailView.as_view(), name='request_detail_api'),
    path('<int:pk>/start/', views.StartRequestView.as_view(), name='start'),
    path('<int:pk>/complete/', views.CompleteRequestView.as_view(), name='complete'),
    path('<int:pk>/resolve/', views.ResolveRequestView.as_view(), name='resolve'),
    path('requests/', views.RequestListView.as_view(), name='request_list_alt'),
    path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
    path('requests/<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:pk>/assign/', views.AssignRequestView.as_view(), name='assign'),
    path('requests/<int:pk>/start/', views.StartRequestView.as_view(), name='start_alt'),
    path('requests/<int:pk>/complete/', views.CompleteRequestView.as_view(), name='complete_alt'),
    path('my-requests/', views.MyRequestsView.as_view(), name='my_requests'),
]
