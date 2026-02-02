from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Staff Profiles
    path('staff-profiles/', views.StaffProfileListCreateView.as_view(), name='staff_profile_list'),
    path('staff-profiles/<int:pk>/', views.StaffProfileDetailView.as_view(), name='staff_profile_detail'),
    path('staff-profiles/department/<int:department_id>/', views.StaffProfileByDepartmentView.as_view(), name='staff_profile_by_department'),
    path('staff-profiles/role/<str:role>/', views.StaffProfileByRoleView.as_view(), name='staff_profile_by_role'),
    
    # Activity Logs
    path('activity-logs/', views.ActivityLogListCreateView.as_view(), name='activity_log_list'),
    path('activity-logs/<int:pk>/', views.ActivityLogDetailView.as_view(), name='activity_log_detail'),
    path('activity-logs/user/<int:user_id>/', views.ActivityLogByUserView.as_view(), name='activity_log_by_user'),
    path('activity-logs/export/', views.ActivityLogExportView.as_view(), name='activity_log_export'),
]
