from rest_framework import serializers
from apps.frontdesk.models import GuestMessage
from django.utils import timezone


class GuestMessageSerializer(serializers.ModelSerializer):
    """Serializer for guest messages."""
    guest_name = serializers.SerializerMethodField()
    room_number = serializers.CharField(source='check_in.room.number', read_only=True)
    taken_by_name = serializers.SerializerMethodField()
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = GuestMessage
        fields = [
            'id', 'check_in', 'guest_name', 'room_number',
            'message_type', 'message_type_display', 'message',
            'from_name', 'from_contact', 'is_delivered',
            'delivered_at', 'taken_by', 'taken_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'delivered_at']
    
    def get_guest_name(self, obj):
        return obj.check_in.guest.get_full_name()
    
    def get_taken_by_name(self, obj):
        return obj.taken_by.get_full_name() if obj.taken_by else None


class GuestMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating guest messages."""
    
    class Meta:
        model = GuestMessage
        fields = [
            'check_in', 'message_type', 'message',
            'from_name', 'from_contact'
        ]
    
    def validate_check_in(self, value):
        """Ensure check_in is valid and guest is in-house."""
        if hasattr(value, 'check_out'):
            raise serializers.ValidationError("Cannot send message to a checked-out guest.")
        return value
    
    def create(self, validated_data):
        # Auto-set taken_by from request
        if self.context.get('request'):
            validated_data['taken_by'] = self.context['request'].user
        return super().create(validated_data)


class GuestMessageReplySerializer(serializers.Serializer):
    """Serializer for replying to guest messages."""
    reply = serializers.CharField(max_length=1000)
