from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # MFA (Multi-Factor Authentication)
    path('mfa/setup/', views.MFASetupView.as_view(), name='mfa_setup'),
    path('mfa/enable/', views.MFAEnableView.as_view(), name='mfa_enable'),
    path('mfa/disable/', views.MFADisableView.as_view(), name='mfa_disable'),
    path('mfa/verify/', views.MFAVerifyView.as_view(), name='mfa_verify'),
    path('mfa/status/', views.MFAStatusView.as_view(), name='mfa_status'),
    path('mfa/resend/', views.MFAResendCodeView.as_view(), name='mfa_resend'),
    
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

    # Password Reset (unauthenticated)
    path('password-reset/request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
