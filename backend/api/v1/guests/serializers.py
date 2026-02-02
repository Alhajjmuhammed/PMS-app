from rest_framework import serializers
from datetime import date
import re
from apps.guests.models import Guest, GuestPreference, GuestDocument, Company, LoyaltyProgram, LoyaltyTier, LoyaltyTransaction


class GuestPreferenceSerializer(serializers.ModelSerializer):
    """Guest preference read serializer."""
    guest_name = serializers.CharField(source='guest.get_full_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = GuestPreference
        fields = ['id', 'guest', 'guest_name', 'category', 'category_display', 'preference', 'notes']
        read_only_fields = ['id']


class GuestPreferenceCreateSerializer(serializers.ModelSerializer):
    """Guest preference write serializer."""
    
    class Meta:
        model = GuestPreference
        fields = ['guest', 'category', 'preference', 'notes']
    
    def validate_preference(self, value):
        """Validate preference text."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Preference must be at least 2 characters.")
        if len(value) > 200:
            raise serializers.ValidationError("Preference text is too long.")
        return value.strip()
    
    def validate(self, data):
        """Check for duplicate preferences."""
        guest = data.get('guest')
        category = data.get('category')
        preference = data.get('preference', '').strip()
        
        # Check if similar preference already exists for this guest
        if self.instance:
            # Update - exclude self
            exists = GuestPreference.objects.filter(
                guest=guest,
                category=category,
                preference__iexact=preference
            ).exclude(id=self.instance.id).exists()
        else:
            # Create
            exists = GuestPreference.objects.filter(
                guest=guest,
                category=category,
                preference__iexact=preference
            ).exists()
        
        if exists:
            raise serializers.ValidationError(
                f"A similar {category} preference already exists for this guest."
            )
        
        return data


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


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model with all fields."""
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'code', 'company_type', 'contact_person',
            'email', 'phone', 'fax', 'website', 'address', 'city', 'country',
            'tax_id', 'credit_limit', 'payment_terms', 'discount_percentage',
            'contract_start', 'contract_end', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_code(self, value):
        """Validate company code uniqueness and format."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Company code must be at least 2 characters.")
        
        value = value.strip().upper()
        
        # Check uniqueness
        instance = self.instance
        if instance:
            # Update case - exclude current instance
            if Company.objects.exclude(pk=instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("A company with this code already exists.")
        else:
            # Create case
            if Company.objects.filter(code=value).exists():
                raise serializers.ValidationError("A company with this code already exists.")
        
        return value
    
    def validate_name(self, value):
        """Validate company name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Company name must be at least 2 characters.")
        if len(value) > 200:
            raise serializers.ValidationError("Company name is too long.")
        return value.strip()
    
    def validate_credit_limit(self, value):
        """Validate credit limit is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Credit limit cannot be negative.")
        return value
    
    def validate_discount_percentage(self, value):
        """Validate discount percentage is between 0 and 100."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Discount percentage must be between 0 and 100.")
        return value
    
    def validate_payment_terms(self, value):
        """Validate payment terms are reasonable."""
        if value < 0 or value > 365:
            raise serializers.ValidationError("Payment terms must be between 0 and 365 days.")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        contract_start = data.get('contract_start')
        contract_end = data.get('contract_end')
        
        if contract_start and contract_end:
            if contract_end < contract_start:
                raise serializers.ValidationError({
                    'contract_end': "Contract end date must be after start date."
                })
        
        return data


class CompanyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for company list view."""
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'code', 'company_type', 'contact_person',
            'email', 'phone', 'is_active', 'credit_limit', 'discount_percentage'
        ]


# ============= Loyalty Program Serializers =============

class LoyaltyTierSerializer(serializers.ModelSerializer):
    """Serializer for loyalty tiers."""
    
    class Meta:
        model = LoyaltyTier
        fields = [
            'id', 'program', 'name', 'min_points', 'benefits',
            'discount_percentage'
        ]
        read_only_fields = ['id']


class LoyaltyProgramSerializer(serializers.ModelSerializer):
    """Serializer for loyalty programs."""
    
    property_name = serializers.CharField(source='property.name', read_only=True)
    tiers = LoyaltyTierSerializer(many=True, read_only=True)
    tier_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LoyaltyProgram
        fields = [
            'id', 'property', 'property_name', 'name', 'description',
            'points_per_currency', 'is_active', 'tiers', 'tier_count'
        ]
        read_only_fields = ['id']
    
    def get_tier_count(self, obj):
        """Get number of tiers."""
        return obj.tiers.count()


class LoyaltyProgramCreateSerializer(serializers.ModelSerializer):
    """Create serializer for loyalty programs."""
    
    class Meta:
        model = LoyaltyProgram
        fields = ['property', 'name', 'description', 'points_per_currency', 'is_active']
    
    def validate_points_per_currency(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Points per currency must be greater than zero"
            )
        return value


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    """Serializer for loyalty transactions."""
    
    guest_name = serializers.CharField(source='guest.full_name', read_only=True)
    guest_email = serializers.CharField(source='guest.email', read_only=True)
    
    class Meta:
        model = LoyaltyTransaction
        fields = [
            'id', 'guest', 'guest_name', 'guest_email', 'transaction_type',
            'points', 'description', 'reference', 'balance_after', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LoyaltyTransactionCreateSerializer(serializers.ModelSerializer):
    """Create serializer for loyalty transactions."""
    
    class Meta:
        model = LoyaltyTransaction
        fields = [
            'guest', 'transaction_type', 'points', 'description', 'reference'
        ]
    
    def validate_points(self, value):
        transaction_type = self.initial_data.get('transaction_type')
        
        if transaction_type == 'REDEEM' and value > 0:
            raise serializers.ValidationError(
                "Redeem transactions must have negative points"
            )
        
        if transaction_type == 'EARN' and value < 0:
            raise serializers.ValidationError(
                "Earn transactions must have positive points"
            )
        
        return value
    
    def create(self, validated_data):
        guest = validated_data['guest']
        points = validated_data['points']
        
        # Calculate new balance
        last_transaction = LoyaltyTransaction.objects.filter(
            guest=guest
        ).order_by('-created_at').first()
        
        current_balance = last_transaction.balance_after if last_transaction else 0
        new_balance = current_balance + points
        
        # Prevent negative balance for redeems
        if new_balance < 0:
            raise serializers.ValidationError(
                f"Insufficient points. Current balance: {current_balance}"
            )
        
        validated_data['balance_after'] = new_balance
        
        return super().create(validated_data)
