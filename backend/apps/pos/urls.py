from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.POSDashboardView.as_view(), name='dashboard'),
    path('outlets/', views.OutletListView.as_view(), name='outlet_list'),
    path('outlets/<int:pk>/', views.OutletDetailView.as_view(), name='outlet_detail'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/post-to-room/', views.PostToRoomView.as_view(), name='post_to_room'),
    path('menu/', views.MenuView.as_view(), name='menu'),
]
