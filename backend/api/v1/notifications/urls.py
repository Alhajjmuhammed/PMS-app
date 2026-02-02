from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_read'),
    path('unread/', views.UnreadNotificationListView.as_view(), name='unread_list'),
    path('register-device/', views.RegisterDeviceView.as_view(), name='register_device'),
    
    # Enhanced Notifications
    path('templates/', views.NotificationTemplateListCreateView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='template_detail'),
    path('emails/', views.EmailLogListCreateView.as_view(), name='email_log_list'),
    path('emails/<int:pk>/', views.EmailLogDetailView.as_view(), name='email_log_detail'),
    path('sms/', views.SMSLogListCreateView.as_view(), name='sms_log_list'),
    path('sms/<int:pk>/', views.SMSLogDetailView.as_view(), name='sms_log_detail'),
    path('push/send/', views.SendPushNotificationView.as_view(), name='send_push'),
]

