from django import forms
from .models import HousekeepingTask, RoomInspection


class HousekeepingTaskForm(forms.ModelForm):
    class Meta:
        model = HousekeepingTask
        fields = ['room', 'task_type', 'priority', 'assigned_to', 'scheduled_date', 'scheduled_time', 'notes', 'special_instructions']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'task_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RoomInspectionForm(forms.ModelForm):
    class Meta:
        model = RoomInspection
        fields = ['cleanliness_score', 'bed_making_score', 'bathroom_score', 'amenities_score', 'overall_score', 'passed', 'notes']
        widgets = {
            'cleanliness_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'bed_making_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'bathroom_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'amenities_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'overall_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'passed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
