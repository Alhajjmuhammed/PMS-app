"""
Serializers for Guests Enhanced Module
"""
from rest_framework import serializers
from apps.guests.models import (
    GuestPreference, GuestDocument, Company,
    LoyaltyProgram, LoyaltyTier, LoyaltyTransaction
)


class GuestPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for guest preferences."""
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = GuestPreference
        ref_name = 'GuestPreferenceDetail'
        fields = [
            'id',
            'guest',
            'category',
            'preference',
            'notes',
            'guest_name', 'category_display'
        
        ]
        
        read_only_fields = ['id']


class GuestDocumentSerializer(serializers.ModelSerializer):
    """Serializer for guest documents."""
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = GuestDocument
        ref_name = 'GuestDocumentDetail'
        fields = [
            'id',
            'guest',
            'document_type',
            'document_number',
            'issuing_country',
            'issue_date',
            'expiry_date',
            'document_file',
            'guest_name', 'document_type_display', 'is_expired'
        
        ]
        
        read_only_fields = ['id']
    
    def get_is_expired(self, obj):
        """Check if document is expired."""
        if obj.expiry_date:
            from datetime import date
            return date.today() > obj.expiry_date
        return False
    
    def validate(self, data):
        """Validate document dates."""
        issue_date = data.get('issue_date')
        expiry_date = data.get('expiry_date')
        
        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                raise serializers.ValidationError(
                    "Expiry date must be after issue date"
                )
        
        return data


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for companies."""
    company_type_display = serializers.CharField(source='get_company_type_display', read_only=True)
    guests_count = serializers.IntegerField(source='guests.count', read_only=True)
    is_contract_active = serializers.SerializerMethodField()
    
    class Meta:
        ref_name = 'CompanySerializerExtended'
        model = Company
        fields = [
            'id',
            'name',
            'code',
            'company_type',
            'contact_person',
            'email',
            'phone',
            'fax',
            'website',
            'address',
            'city',
            'country',
            'tax_id',
            'credit_limit',
            'payment_terms',
            'discount_percentage',
            'contract_start',
            'contract_end',
            'is_active',
            'notes',
            'created_at',
            'updated_at',
            'company_type_display', 'guests_count', 'is_contract_active'
        
        ]
        
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_contract_active(self, obj):
        """Check if contract is currently active."""
        if obj.contract_start and obj.contract_end:
            from datetime import date
            today = date.today()
            return obj.contract_start <= today <= obj.contract_end
        return None
    
    def validate_code(self, value):
        """Ensure company code is unique."""
        if self.instance:
            if Company.objects.exclude(id=self.instance.id).filter(code=value).exists():
                raise serializers.ValidationError("Company code must be unique")
        else:
            if Company.objects.filter(code=value).exists():
                raise serializers.ValidationError("Company code must be unique")
        return value
    
    def validate(self, data):
        """Validate company data."""
        # Validate contract dates
        contract_start = data.get('contract_start')
        contract_end = data.get('contract_end')
        
        if contract_start and contract_end:
            if contract_end <= contract_start:
                raise serializers.ValidationError(
                    "Contract end date must be after start date"
                )
        
        # Validate discount percentage
        discount = data.get('discount_percentage', 0)
        if discount < 0 or discount > 100:
            raise serializers.ValidationError(
                "Discount percentage must be between 0 and 100"
            )
        
        return data


class LoyaltyProgramSerializer(serializers.ModelSerializer):
    """Serializer for loyalty programs."""
    tiers_count = serializers.IntegerField(source='tiers.count', read_only=True)
    
    class Meta:
        ref_name = 'LoyaltyProgramSerializerExtended'
        model = LoyaltyProgram
        fields = [
            'id',
            'property',
            'name',
            'description',
            'points_per_currency',
            'is_active',
            'tiers_count'
        
        ]
        
        read_only_fields = ['id']
    
    def validate_points_per_currency(self, value):
        """Validate points per currency is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Points per currency must be greater than 0"
            )
        return value


class LoyaltyTierSerializer(serializers.ModelSerializer):
    """Serializer for loyalty tiers."""
    program_name = serializers.CharField(source='program.name', read_only=True)
    
    class Meta:
        ref_name = 'LoyaltyTierSerializerExtended'
        model = LoyaltyTier
        fields = [
            'id',
            'program',
            'name',
            'min_points',
            'benefits',
            'discount_percentage',
            'program_name'
        
        ]
        
        read_only_fields = ['id']
    
    def validate_min_points(self, value):
        """Validate min points is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Minimum points cannot be negative")
        return value
    
    def validate_discount_percentage(self, value):
        """Validate discount percentage."""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Discount percentage must be between 0 and 100"
            )
        return value


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    """Serializer for loyalty transactions."""
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display', read_only=True
    )
    
    class Meta:
        ref_name = 'LoyaltyTransactionSerializerExtended'
        model = LoyaltyTransaction
        fields = [
            'id',
            'guest',
            'transaction_type',
            'points',
            'description',
            'reference',
            'balance_after',
            'created_at',
            'guest_name', 'transaction_type_display'
        
        ]
        
        read_only_fields = ['id', 'balance_after', 'created_at']
    
    def validate_points(self, value):
        """Validate points value based on transaction type."""
        transaction_type = self.initial_data.get('transaction_type')
        
        if transaction_type == 'EARN' and value < 0:
            raise serializers.ValidationError("Earn points must be positive")
        if transaction_type == 'REDEEM' and value > 0:
            raise serializers.ValidationError("Redeem points must be negative")
        
        return value
    
    def create(self, validated_data):
        """Create transaction and update guest balance."""
        guest = validated_data['guest']
        points = validated_data['points']
        
        # Update guest loyalty points
        guest.loyalty_points += points
        if guest.loyalty_points < 0:
            raise serializers.ValidationError(
                "Insufficient loyalty points"
            )
        
        validated_data['balance_after'] = guest.loyalty_points
        guest.save()
        
        return super().create(validated_data)


class GuestLoyaltySerializer(serializers.Serializer):
    """Serializer for guest loyalty dashboard."""
    guest_id = serializers.IntegerField()
    guest_name = serializers.CharField()
    loyalty_number = serializers.CharField()
    loyalty_tier = serializers.CharField()
    loyalty_points = serializers.IntegerField()
    total_earned = serializers.IntegerField()
    total_redeemed = serializers.IntegerField()
    recent_transactions = LoyaltyTransactionSerializer(many=True)
