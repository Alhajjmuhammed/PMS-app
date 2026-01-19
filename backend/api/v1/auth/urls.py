from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # User management
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Role and permission management
    path('permissions/', views.PermissionListView.as_view(), name='permission_list'),
    path('roles/', views.RoleListCreateView.as_view(), name='role_list_create'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
]
