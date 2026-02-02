"""
URLs for POS API
"""
from django.urls import path
from . import views
from . import pos_views

app_name = 'pos'

urlpatterns = [
    # ===== Outlets =====
    path('outlets/', pos_views.OutletListView.as_view(), name='outlet_list'),
    
    # ===== Menu Categories =====
    path('categories/', pos_views.MenuCategoryListCreateView.as_view(), name='category_list'),
    path('categories/<int:pk>/', pos_views.MenuCategoryDetailView.as_view(), name='category_detail'),
    
    # ===== Menu Items =====
    path('menu-items/', pos_views.MenuItemListCreateView.as_view(), name='menu_item_list'),
    path('menu-items/<int:pk>/', pos_views.MenuItemDetailView.as_view(), name='menu_item_detail'),
    path('menu-items/category/<int:category_id>/', pos_views.MenuItemsByCategoryView.as_view(), name='menu_items_by_category'),
    path('menu-items/available/', pos_views.AvailableMenuItemsView.as_view(), name='available_menu_items'),
    
    # ===== POS Orders =====
    path('orders/', pos_views.POSOrderListCreateView.as_view(), name='order_list'),
    path('orders/<int:pk>/', pos_views.POSOrderDetailView.as_view(), name='order_detail'),
    path('orders/open/', pos_views.OpenPOSOrdersView.as_view(), name='open_orders'),
    path('orders/<int:pk>/close/', pos_views.ClosePOSOrderView.as_view(), name='close_order'),
    path('orders/<int:pk>/post-to-room/', pos_views.PostToRoomView.as_view(), name='post_to_room'),
    
    # ===== POS Order Items =====
    path('orders/<int:order_id>/items/', pos_views.POSOrderItemListView.as_view(), name='order_items'),
    path('order-items/', pos_views.POSOrderItemCreateView.as_view(), name='order_item_create'),
    
    # ===== Dashboard =====
    path('dashboard/', pos_views.POSDashboardView.as_view(), name='dashboard'),
    
    # ===== Legacy compatibility =====
    path('outlets/<int:pk>/', views.OutletDetailView.as_view(), name='outlet_detail'),
    path('outlets/<int:pk>/menu/', views.MenuView.as_view(), name='menu'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/add-item/', views.AddItemView.as_view(), name='add_item'),
]
