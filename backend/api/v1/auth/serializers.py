from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='assigned_property.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'assigned_property', 'property_name', 'phone', 'is_active',
            'last_login', 'date_joined'
        ]
        read_only_fields = ['id', 'is_active', 'last_login', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class UserManagementSerializer(serializers.ModelSerializer):
    """Serializer for user management (admin operations)."""
    property_name = serializers.CharField(source='assigned_property.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'assigned_property', 'property_name', 'phone', 'is_active',
            'is_staff', 'last_login', 'date_joined', 'password'
        ]
        read_only_fields = ['id', 'last_login', 'date_joined']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class PermissionSerializer(serializers.Serializer):
    """Serializer for Django permissions."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    codename = serializers.CharField()
    content_type = serializers.SerializerMethodField()
    
    def get_content_type(self, obj):
        return obj.content_type.app_label if obj.content_type else None


class RoleSerializer(serializers.Serializer):
    """Serializer for Django groups (roles)."""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    permissions = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
