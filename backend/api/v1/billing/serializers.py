from rest_framework import serializers
from apps.billing.models import Folio, FolioCharge, Payment, ChargeCode


class ChargeCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeCode
        fields = ['id', 'code', 'name', 'category', 'default_amount']


class FolioChargeSerializer(serializers.ModelSerializer):
    charge_code_name = serializers.CharField(source='charge_code.name', read_only=True)
    
    class Meta:
        model = FolioCharge
        fields = [
            'id', 'charge_code', 'charge_code_name', 'description',
            'quantity', 'unit_price', 'amount', 'tax_amount', 'total',
            'charge_date', 'is_voided'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_method', 'amount', 'reference_number',
            'card_last_four', 'payment_date', 'is_voided'
        ]


class FolioSerializer(serializers.ModelSerializer):
    charges = FolioChargeSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    room_number = serializers.SerializerMethodField()
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Folio
        fields = [
            'id', 'folio_number', 'folio_type', 'status', 'guest', 'guest_name',
            'room_number', 'total_charges', 'total_taxes', 'total_payments',
            'balance', 'charges', 'payments', 'open_date', 'close_date',
            'created_at', 'updated_at'
        ]
    
    def get_room_number(self, obj):
        if obj.reservation and hasattr(obj.reservation, 'rooms') and obj.reservation.rooms.exists():
            room_reservation = obj.reservation.rooms.first()
            return room_reservation.room.room_number if room_reservation.room else ''
        return ''


class AddChargeSerializer(serializers.Serializer):
    charge_code_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    quantity = serializers.IntegerField(default=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class AddPaymentSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reference_number = serializers.CharField(required=False, allow_blank=True)
    card_last_four = serializers.CharField(required=False, allow_blank=True, max_length=4)


class InvoiceSerializer(serializers.ModelSerializer):
    """Invoice serializer."""
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        from apps.billing.models import Invoice
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer_name', 'status',
            'subtotal', 'tax_amount', 'discount_amount', 'total_amount',
            'paid_amount', 'balance', 'issue_date', 'due_date',
            'created_at', 'updated_at'
        ]
    
    def get_customer_name(self, obj):
        if hasattr(obj, 'folio') and obj.folio and obj.folio.guest:
            return obj.folio.guest.full_name if hasattr(obj.folio.guest, 'full_name') else f"{obj.folio.guest.first_name} {obj.folio.guest.last_name}"
        return ''


class PaymentSerializer(serializers.ModelSerializer):
    """Payment serializer."""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'folio', 'payment_method', 'amount', 'status',
            'reference_number', 'card_last_four', 'payment_date',
            'processed_by', 'notes', 'created_at'
        ]
