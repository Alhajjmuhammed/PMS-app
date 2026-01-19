from django import forms
from apps.rooms.models import Room
from .models import CheckIn, CheckOut, RoomMove, WalkIn, GuestMessage


class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = [
            'room', 'expected_check_out', 'id_type', 'id_number', 'id_expiry',
            'key_card_number', 'keys_issued', 'deposit_amount', 'deposit_method',
            'registration_card', 'notes'
        ]
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'expected_check_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'id_type': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'key_card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'keys_issued': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'deposit_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'deposit_method': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_card': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CheckOutForm(forms.ModelForm):
    class Meta:
        model = CheckOut
        fields = ['total_charges', 'total_payments', 'balance', 'keys_returned', 'rating', 'feedback', 'notes']
        widgets = {
            'total_charges': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'total_payments': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'keys_returned': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RoomMoveForm(forms.Form):
    to_room = forms.ModelChoiceField(
        queryset=Room.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    reason = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['to_room'].queryset = Room.objects.filter(
            status=Room.RoomStatus.VACANT_CLEAN,
            fo_status=Room.FrontOfficeStatus.VACANT,
            is_active=True
        )


class WalkInForm(forms.ModelForm):
    class Meta:
        model = WalkIn
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'room_type', 'check_in_date', 'check_out_date',
            'adults', 'children', 'rate_per_night', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'rate_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class GuestMessageForm(forms.ModelForm):
    class Meta:
        model = GuestMessage
        fields = ['message_type', 'message', 'from_name', 'from_contact']
        widgets = {
            'message_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'from_name': forms.TextInput(attrs={'class': 'form-control'}),
            'from_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
