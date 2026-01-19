from django import forms
from django.forms import inlineformset_factory
from .models import Reservation, ReservationRoom, GroupBooking


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'guest', 'company', 'check_in_date', 'check_out_date',
            'arrival_time', 'departure_time', 'status', 'source',
            'adults', 'children', 'infants', 'rate_plan',
            'special_requests', 'internal_notes',
            'total_amount', 'deposit_amount', 'deposit_paid'
        ]
        widgets = {
            'guest': forms.Select(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'infants': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rate_plan': forms.Select(attrs={'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReservationRoomForm(forms.ModelForm):
    class Meta:
        model = ReservationRoom
        fields = ['room_type', 'room', 'rate_per_night', 'adults', 'children', 'guest_name']
        widgets = {
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-control'}),
            'rate_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'guest_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


ReservationRoomFormSet = inlineformset_factory(
    Reservation,
    ReservationRoom,
    form=ReservationRoomForm,
    extra=1,
    can_delete=True
)


class GroupBookingForm(forms.ModelForm):
    class Meta:
        model = GroupBooking
        fields = [
            'name', 'code', 'contact_name', 'contact_email', 'contact_phone',
            'company', 'check_in_date', 'check_out_date', 'cutoff_date',
            'rooms_blocked', 'status', 'group_rate', 'deposit_required', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.Select(attrs={'class': 'form-control'}),
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cutoff_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rooms_blocked': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'group_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit_required': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
