from rest_framework import serializers
from apps.accounts.models import StaffProfile, ActivityLog
from django.contrib.auth import get_user_model

User = get_user_model()


# ===========================
# MFA Serializers
# ===========================

class MFASetupSerializer(serializers.Serializer):
    """Serializer for MFA setup initiation."""
    method = serializers.ChoiceField(
        choices=['TOTP', 'EMAIL', 'SMS'],
        default='TOTP',
        help_text="MFA method to set up"
    )


class MFASetupResponseSerializer(serializers.Serializer):
    """Response serializer for MFA setup."""
    secret = serializers.CharField(help_text="TOTP secret (for TOTP method)")
    qr_code = serializers.CharField(help_text="Base64 encoded QR code (for TOTP method)")
    backup_codes = serializers.ListField(
        child=serializers.CharField(),
        help_text="Backup recovery codes"
    )
    method = serializers.CharField(help_text="MFA method")


class MFAVerifySerializer(serializers.Serializer):
    """Serializer for MFA code verification."""
    code = serializers.CharField(
        max_length=8,
        min_length=6,
        help_text="6-digit MFA code or 8-character backup code"
    )


class MFAEnableSerializer(serializers.Serializer):
    """Serializer for enabling MFA after verification."""
    code = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text="6-digit verification code"
    )
    method = serializers.ChoiceField(
        choices=['TOTP', 'EMAIL', 'SMS'],
        help_text="MFA method to enable"
    )


class MFALoginSerializer(serializers.Serializer):
    """Serializer for MFA login verification."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mfa_code = serializers.CharField(
        max_length=8,
        required=False,
        help_text="MFA code (required if MFA enabled)"
    )


class UserMFAStatusSerializer(serializers.ModelSerializer):
    """Serializer for user MFA status."""
    
    class Meta:
        model = User
        fields = ['mfa_enabled', 'mfa_method']
        read_only_fields = ['mfa_enabled', 'mfa_method']


# ===========================
# Staff Profile Serializers
# ===========================

class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for staff profile management."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    user_role = serializers.CharField(source='user.role', read_only=True)
    department_name = serializers.CharField(source='user.department.name', read_only=True)
    property_name = serializers.CharField(source='user.assigned_property.name', read_only=True)
    
    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'user_email', 'user_name', 'user_role',
            'employee_id', 'hire_date', 'job_title',
            'emergency_contact', 'emergency_phone', 'address',
            'department_name', 'property_name', 'notes'
        ]
        read_only_fields = ['id']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()


class StaffProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating staff profiles with user selection."""
    
    class Meta:
        model = StaffProfile
        fields = [
            'user', 'employee_id', 'hire_date', 'job_title',
            'emergency_contact', 'emergency_phone', 'address', 'notes'
        ]
    
    def validate_user(self, value):
        """Ensure user doesn't already have a staff profile."""
        if StaffProfile.objects.filter(user=value).exists():
            raise serializers.ValidationError("This user already has a staff profile.")
        return value
    
    def validate_employee_id(self, value):
        """Ensure employee ID is unique."""
        if self.instance:
            # Update case - exclude current instance
            if StaffProfile.objects.filter(employee_id=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("This employee ID is already in use.")
        else:
            # Create case
            if StaffProfile.objects.filter(employee_id=value).exists():
                raise serializers.ValidationError("This employee ID is already in use.")
        return value


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for activity logs."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_email', 'user_name', 'action', 'action_display',
            'model_name', 'object_id', 'description',
            'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else 'System'


class ActivityLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating activity logs."""
    
    class Meta:
        model = ActivityLog
        fields = [
            'user', 'action', 'model_name', 'object_id', 'description',
            'ip_address', 'user_agent'
        ]
    
    def create(self, validated_data):
        # Auto-set user from request if not provided
        if 'user' not in validated_data and self.context.get('request'):
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
