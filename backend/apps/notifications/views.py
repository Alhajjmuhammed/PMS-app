from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.http import JsonResponse
from django.utils import timezone
from .models import NotificationTemplate, Notification, EmailLog, Alert, SMSLog


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 30
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('notifications:list')


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')


class TemplateListView(LoginRequiredMixin, ListView):
    model = NotificationTemplate
    template_name = 'notifications/template_list.html'
    context_object_name = 'templates'


class TemplateDetailView(LoginRequiredMixin, DetailView):
    model = NotificationTemplate
    template_name = 'notifications/template_detail.html'
    context_object_name = 'template'


class AlertListView(LoginRequiredMixin, ListView):
    model = Alert
    template_name = 'notifications/alert_list.html'
    context_object_name = 'alerts'
    
    def get_queryset(self):
        return Alert.objects.filter(is_active=True)


class AlertCreateView(LoginRequiredMixin, View):
    template_name = 'notifications/alert_create.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        Alert.objects.create(
            property=request.user.property,
            alert_type=request.POST.get('alert_type', 'INFO'),
            title=request.POST.get('title'),
            message=request.POST.get('message'),
            created_by=request.user
        )
        messages.success(request, 'Alert created.')
        return redirect('notifications:alert_list')


class EmailLogListView(LoginRequiredMixin, ListView):
    model = EmailLog
    template_name = 'notifications/email_log.html'
    context_object_name = 'emails'
    paginate_by = 50


class SMSLogListView(LoginRequiredMixin, ListView):
    model = SMSLog
    template_name = 'notifications/sms_log.html'
    context_object_name = 'messages'
    paginate_by = 50


# Utility function for sending notifications
def send_notification(user, title, message, priority='NORMAL', link=''):
    """Create a notification for a user."""
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        priority=priority,
        link=link
    )


def send_email(to_email, subject, body, template=None, related_type='', related_id=None):
    """Log email for sending."""
    return EmailLog.objects.create(
        template=template,
        to_email=to_email,
        subject=subject,
        body=body,
        related_object_type=related_type,
        related_object_id=related_id
    )
