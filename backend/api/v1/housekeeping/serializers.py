from rest_framework import serializers
from apps.housekeeping.models import HousekeepingTask, RoomInspection


class HousekeepingTaskSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    room_type = serializers.CharField(source='room.room_type.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = HousekeepingTask
        fields = [
            'id', 'room', 'room_number', 'room_type', 'task_type', 'status',
            'priority', 'assigned_to', 'assigned_to_name',
            'scheduled_date', 'started_at', 'completed_at',
            'notes', 'special_instructions'
        ]


class TaskUpdateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class RoomInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInspection
        fields = [
            'id', 'task', 'inspected_by', 'inspection_time',
            'cleanliness_score', 'amenities_score', 'overall_score',
            'passed', 'comments'
        ]
