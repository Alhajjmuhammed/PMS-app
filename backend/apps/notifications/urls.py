from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('mark-read/<int:pk>/', views.MarkReadView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('templates/<int:pk>/', views.TemplateDetailView.as_view(), name='template_detail'),
    path('alerts/', views.AlertListView.as_view(), name='alert_list'),
    path('alerts/create/', views.AlertCreateView.as_view(), name='alert_create'),
    path('email-log/', views.EmailLogListView.as_view(), name='email_log'),
    path('sms-log/', views.SMSLogListView.as_view(), name='sms_log'),
]
