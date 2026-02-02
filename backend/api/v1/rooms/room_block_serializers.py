from rest_framework import serializers
from apps.rooms.models import RoomBlock
from django.utils import timezone


class RoomBlockSerializer(serializers.ModelSerializer):
    """Serializer for room blocks."""
    room_number = serializers.CharField(source='room.number', read_only=True)
    room_type_name = serializers.CharField(source='room.room_type.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    duration_days = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomBlock
        fields = [
            'id', 'room', 'room_number', 'room_type_name',
            'reason', 'reason_display', 'start_date', 'end_date',
            'duration_days', 'is_active', 'notes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None
    
    def get_duration_days(self, obj):
        return (obj.end_date - obj.start_date).days + 1
    
    def get_is_active(self, obj):
        today = timezone.now().date()
        return obj.start_date <= today <= obj.end_date
    
    def validate(self, data):
        """Validate date range."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        # Check for overlapping blocks
        room = data.get('room')
        if room:
            overlapping = RoomBlock.objects.filter(
                room=room,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            # Exclude current instance if updating
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            
            if overlapping.exists():
                raise serializers.ValidationError({
                    'room': 'This room is already blocked during the selected period.'
                })
        
        return data


class RoomBlockCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating room blocks."""
    
    class Meta:
        model = RoomBlock
        fields = [
            'room', 'reason', 'start_date', 'end_date', 'notes'
        ]
    
    def validate(self, data):
        """Validate date range and overlaps."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        # Check for overlapping blocks
        room = data.get('room')
        if room:
            overlapping = RoomBlock.objects.filter(
                room=room,
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            if overlapping.exists():
                raise serializers.ValidationError({
                    'room': 'This room is already blocked during the selected period.'
                })
        
        return data
    
    def create(self, validated_data):
        # Auto-set created_by from request
        if self.context.get('request'):
            validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
