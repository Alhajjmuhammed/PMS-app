from rest_framework import serializers
from apps.notifications.models import (
    Notification, PushDeviceToken, NotificationTemplate,
    EmailLog, SMSLog
)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class PushDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushDeviceToken
        fields = ['id', 'token', 'platform', 'device_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


# ============= Enhanced Notifications Serializers =============

class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Notification template read serializer."""
    property_name = serializers.CharField(source='property.name', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    trigger_event_display = serializers.CharField(source='get_trigger_event_display', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'property', 'property_name', 'name', 'template_type',
            'template_type_display', 'trigger_event', 'trigger_event_display',
            'subject', 'body', 'html_body', 'is_active'
        ]
        read_only_fields = ['id']


class NotificationTemplateCreateSerializer(serializers.ModelSerializer):
    """Notification template write serializer."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'property', 'name', 'template_type', 'trigger_event',
            'subject', 'body', 'html_body', 'is_active'
        ]
    
    def validate(self, data):
        """Validate template fields based on type."""
        template_type = data.get('template_type')
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        # Email templates require subject
        if template_type == 'EMAIL' and not subject:
            raise serializers.ValidationError({
                'subject': 'Email templates require a subject.'
            })
        
        # All templates require body
        if not body:
            raise serializers.ValidationError({
                'body': 'Template body is required.'
            })
        
        # SMS templates should have shorter body
        if template_type == 'SMS' and len(body) > 160:
            raise serializers.ValidationError({
                'body': 'SMS template body should not exceed 160 characters.'
            })
        
        return data


class EmailLogSerializer(serializers.ModelSerializer):
    """Email log read serializer."""
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'template', 'template_name', 'to_email', 'cc_email',
            'subject', 'body', 'status', 'status_display', 'error_message',
            'sent_at', 'created_at', 'related_object_type', 'related_object_id'
        ]
        read_only_fields = ['id', 'sent_at', 'created_at']


class EmailLogCreateSerializer(serializers.ModelSerializer):
    """Email log write serializer."""
    
    class Meta:
        model = EmailLog
        fields = [
            'template', 'to_email', 'cc_email', 'subject', 'body',
            'related_object_type', 'related_object_id'
        ]
    
    def validate_to_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError('Recipient email is required.')
        return value
    
    def validate(self, data):
        """Validate email fields."""
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        if not subject:
            raise serializers.ValidationError({
                'subject': 'Email subject is required.'
            })
        
        if not body:
            raise serializers.ValidationError({
                'body': 'Email body is required.'
            })
        
        return data


class SMSLogSerializer(serializers.ModelSerializer):
    """SMS log read serializer."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SMSLog
        fields = [
            'id', 'to_number', 'message', 'status', 'status_display',
            'provider_message_id', 'error_message', 'sent_at',
            'delivered_at', 'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'delivered_at', 'created_at']


class SMSLogCreateSerializer(serializers.ModelSerializer):
    """SMS log write serializer."""
    
    class Meta:
        model = SMSLog
        fields = ['to_number', 'message']
    
    def validate_message(self, value):
        """Validate SMS message length."""
        if not value:
            raise serializers.ValidationError('Message is required.')
        
        if len(value) > 160:
            raise serializers.ValidationError(
                'Message should not exceed 160 characters for standard SMS.'
            )
        
        return value
    
    def validate_to_number(self, value):
        """Validate phone number format."""
        if not value:
            raise serializers.ValidationError('Phone number is required.')
        
        # Remove common formatting characters
        cleaned = value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        if not cleaned.isdigit():
            raise serializers.ValidationError('Phone number should contain only digits.')
        
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise serializers.ValidationError(
                'Phone number should be between 10 and 15 digits.'
            )
        
        return value


class PushNotificationSerializer(serializers.Serializer):
    """Push notification send serializer."""
    user_id = serializers.IntegerField(required=False)
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    title = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=500)
    data = serializers.JSONField(required=False)
    priority = serializers.ChoiceField(
        choices=['LOW', 'NORMAL', 'HIGH', 'URGENT'],
        default='NORMAL'
    )
    
    def validate(self, data):
        """Ensure either user_id or user_ids is provided."""
        if not data.get('user_id') and not data.get('user_ids'):
            raise serializers.ValidationError(
                'Either user_id or user_ids must be provided.'
            )
        return data
