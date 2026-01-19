from rest_framework import serializers
from datetime import date
import re
from apps.guests.models import Guest, GuestPreference, GuestDocument


class GuestPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestPreference
        fields = ['id', 'category', 'preference', 'notes']


class GuestSerializer(serializers.ModelSerializer):
    preferences = GuestPreferenceSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Guest
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'date_of_birth', 'gender', 'nationality', 'id_type', 'id_number',
            'address', 'city', 'state', 'country', 'postal_code',
            'vip_level', 'is_blacklisted', 'total_stays', 'total_revenue',
            'preferences', 'created_at'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class GuestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'gender', 'nationality',
            'id_type', 'id_number',
            'address', 'city', 'state', 'country', 'postal_code'
        ]
    
    def validate_first_name(self, value):
        """Validate first name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters.")
        if len(value) > 100:
            raise serializers.ValidationError("First name is too long.")
        if not re.match(r'^[a-zA-Z\s\'-]+$', value):
            raise serializers.ValidationError("First name contains invalid characters.")
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters.")
        if len(value) > 100:
            raise serializers.ValidationError("Last name is too long.")
        if not re.match(r'^[a-zA-Z\s\'-]+$', value):
            raise serializers.ValidationError("Last name contains invalid characters.")
        return value.strip()
    
    def validate_email(self, value):
        """Validate email uniqueness and format."""
        if Guest.objects.filter(email=value).exists():
            raise serializers.ValidationError("A guest with this email already exists.")
        return value.lower()
    
    def validate_phone(self, value):
        """Validate phone number."""
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\+]', '', value)
        if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
            raise serializers.ValidationError("Invalid phone number format.")
        return value
    
    def validate_date_of_birth(self, value):
        """Validate date of birth."""
        if value:
            if value > date.today():
                raise serializers.ValidationError("Date of birth cannot be in the future.")
            age = (date.today() - value).days // 365
            if age < 18:
                raise serializers.ValidationError("Guest must be at least 18 years old.")
            if age > 120:
                raise serializers.ValidationError("Invalid date of birth.")
        return value
    
    def validate_id_number(self, value):
        """Validate ID number."""
        if value:
            if len(value) < 5:
                raise serializers.ValidationError("ID number is too short.")
            if len(value) > 50:
                raise serializers.ValidationError("ID number is too long.")
        return value
    
    def validate_postal_code(self, value):
        """Validate postal code."""
        if value and len(value) > 20:
            raise serializers.ValidationError("Postal code is too long.")
        return value


class GuestDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = GuestDocument
        fields = ['id', 'document_type', 'document_file', 'description', 'uploaded_at', 'uploaded_by', 'uploaded_by_name', 'file_size']
        read_only_fields = ['uploaded_at', 'uploaded_by', 'uploaded_by_name']
    
    def get_file_size(self, obj):
        """Return file size in bytes."""
        if obj.document_file:
            return obj.document_file.size
        return None
