from django import forms
from .models import RoomType, Room, RoomBlock, RoomAmenity


class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = [
            'name', 'code', 'description', 'max_occupancy', 'max_adults', 'max_children',
            'size_sqm', 'bed_type', 'base_rate', 'extra_adult_rate', 'extra_child_rate',
            'image', 'sort_order', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_occupancy': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_adults': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_children': forms.NumberInput(attrs={'class': 'form-control'}),
            'size_sqm': forms.NumberInput(attrs={'class': 'form-control'}),
            'bed_type': forms.TextInput(attrs={'class': 'form-control'}),
            'base_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'extra_adult_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'extra_child_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_type', 'building', 'floor', 'room_number', 'name', 'description',
            'status', 'fo_status', 'is_smoking', 'is_accessible', 'is_connecting',
            'connecting_room', 'is_active', 'notes'
        ]
        widgets = {
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'building': forms.Select(attrs={'class': 'form-control'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'fo_status': forms.Select(attrs={'class': 'form-control'}),
            'is_smoking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_accessible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_connecting': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'connecting_room': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RoomStatusForm(forms.ModelForm):
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    
    class Meta:
        model = Room
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class RoomBlockForm(forms.ModelForm):
    class Meta:
        model = RoomBlock
        fields = ['room', 'reason', 'start_date', 'end_date', 'notes']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
