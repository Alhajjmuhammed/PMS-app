from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('outlets/', views.OutletListView.as_view(), name='outlet_list'),
    path('outlets/<int:pk>/', views.OutletDetailView.as_view(), name='outlet_detail'),
    path('outlets/<int:pk>/menu/', views.MenuView.as_view(), name='menu'),
    path('outlets/<int:outlet_id>/categories/', views.MenuCategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.MenuCategoryDetailView.as_view(), name='category_detail'),
    path('menu-items/', views.MenuItemListView.as_view(), name='menu_item_list'),
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu_item_detail'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/add-item/', views.AddItemView.as_view(), name='add_item'),
    path('orders/<int:pk>/post-to-room/', views.PostToRoomView.as_view(), name='post_to_room'),
]
