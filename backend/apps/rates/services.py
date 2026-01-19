"""
Pricing Service
Handles dynamic rate calculation with seasons, discounts, packages, and yield rules
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Q
from apps.rates.models import RatePlan, Season, RoomRate, Discount, Package, YieldRule


class PricingService:
    """Service for calculating dynamic prices."""
    
    @staticmethod
    def calculate_room_rate(room_type_id, rate_plan_id, check_in_date, check_out_date, adults=1, children=0):
        """
        Calculate total room rate for a stay.
        
        Args:
            room_type_id: Room type ID
            rate_plan_id: Rate plan ID
            check_in_date: Check-in date
            check_out_date: Check-out date
            adults: Number of adults
            children: Number of children
            
        Returns:
            dict: Pricing breakdown
        """
        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            return {'error': 'Invalid date range'}
        
        try:
            rate_plan = RatePlan.objects.get(id=rate_plan_id, is_active=True)
        except RatePlan.DoesNotExist:
            return {'error': 'Rate plan not found'}
        
        # Calculate daily rates
        daily_rates = []
        total_base = Decimal('0')
        current_date = check_in_date
        
        while current_date < check_out_date:
            # Get applicable season
            season = PricingService._get_season(rate_plan.property_id, current_date)
            
            # Get room rate for this season
            try:
                if season:
                    room_rate = RoomRate.objects.get(
                        rate_plan=rate_plan,
                        room_type_id=room_type_id,
                        season=season,
                        is_active=True
                    )
                else:
                    room_rate = RoomRate.objects.get(
                        rate_plan=rate_plan,
                        room_type_id=room_type_id,
                        season__isnull=True,
                        is_active=True
                    )
            except RoomRate.DoesNotExist:
                return {'error': f'No rate found for date {current_date}'}
            
            # Calculate daily rate based on occupancy
            if adults <= 2:
                daily_rate = room_rate.double_rate if adults == 2 else room_rate.single_rate
            else:
                daily_rate = room_rate.double_rate + (room_rate.extra_adult * (adults - 2))
            
            if children > 0:
                daily_rate += room_rate.extra_child * children
            
            # Apply yield management
            daily_rate = PricingService._apply_yield_rules(
                rate_plan.property_id, 
                room_type_id,
                current_date,
                daily_rate
            )
            
            daily_rates.append({
                'date': current_date.isoformat(),
                'rate': float(daily_rate),
                'season': season.name if season else 'Standard'
            })
            
            total_base += daily_rate
            current_date += timedelta(days=1)
        
        # Apply discounts
        discount_amount, discount_details = PricingService._calculate_discounts(
            rate_plan.property_id,
            rate_plan_id,
            total_base,
            nights,
            check_in_date
        )
        
        # Apply packages
        package_value, package_details = PricingService._apply_packages(
            rate_plan_id,
            nights
        )
        
        subtotal = total_base - discount_amount
        tax_rate = Decimal('0.15')  # 15% tax (configure per property)
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount + package_value
        
        return {
            'nights': nights,
            'adults': adults,
            'children': children,
            'daily_rates': daily_rates,
            'base_amount': float(total_base),
            'discount_amount': float(discount_amount),
            'discount_details': discount_details,
            'package_value': float(package_value),
            'package_details': package_details,
            'subtotal': float(subtotal),
            'tax_rate': float(tax_rate),
            'tax_amount': float(tax_amount),
            'total_amount': float(total),
            'average_per_night': float(total / nights) if nights > 0 else 0,
        }
    
    @staticmethod
    def _get_season(property_id, date):
        """Get applicable season for a date."""
        seasons = Season.objects.filter(
            property_id=property_id,
            is_active=True,
            start_date__lte=date,
            end_date__gte=date
        ).order_by('-priority')
        
        return seasons.first()
    
    @staticmethod
    def _apply_yield_rules(property_id, room_type_id, date, base_rate):
        """Apply yield management rules to adjust pricing."""
        rules = YieldRule.objects.filter(
            property_id=property_id,
            is_active=True
        )
        
        for rule in rules:
            # Apply rules based on trigger type
            if rule.trigger_type == 'OCCUPANCY':
                # Would need actual occupancy calculation
                # For now, apply adjustment
                base_rate = base_rate * (Decimal('1') + rule.adjustment_percent / 100)
            elif rule.trigger_type == 'DAY_AHEAD':
                # Calculate days until check-in
                days_until = (date - datetime.now().date()).days
                if rule.min_threshold <= days_until:
                    if rule.max_threshold is None or days_until <= rule.max_threshold:
                        base_rate = base_rate * (Decimal('1') + rule.adjustment_percent / 100)
            elif rule.trigger_type == 'DEMAND':
                # Would need demand calculation
                pass
        
        return base_rate
    
    @staticmethod
    def _calculate_discounts(property_id, rate_plan_id, base_amount, nights, check_in_date):
        """Calculate applicable discounts."""
        discount_amount = Decimal('0')
        discount_details = []
        
        # Get applicable discounts
        discounts = Discount.objects.filter(
            property_id=property_id,
            is_active=True,
            valid_from__lte=check_in_date,
            valid_to__gte=check_in_date
        )
        
        for discount in discounts:
            amount = Decimal('0')
            applies = False
            
            # Check if discount applies
            if discount.min_nights and nights < discount.min_nights:
                continue
            
            # Calculate discount
            if discount.discount_type == 'PERCENTAGE':
                amount = base_amount * (discount.value / 100)
                applies = True
            elif discount.discount_type == 'FIXED':
                amount = discount.value
                applies = True
            
            if applies:
                discount_amount += amount
                discount_details.append({
                    'name': discount.name,
                    'type': discount.discount_type,
                    'amount': float(amount)
                })
        
        return discount_amount, discount_details
    
    @staticmethod
    def _apply_packages(rate_plan_id, nights):
        """Apply package additions."""
        # Packages functionality can be added later
        # For now, return empty values
        package_value = Decimal('0')
        package_details = []
        
        return package_value, package_details
    
    @staticmethod
    def get_rate_comparison(room_type_id, check_in_date, check_out_date, property_id):
        """Compare rates across all available rate plans."""
        rate_plans = RatePlan.objects.filter(
            property_id=property_id,
            is_active=True
        )
        
        comparisons = []
        for rate_plan in rate_plans:
            pricing = PricingService.calculate_room_rate(
                room_type_id, 
                rate_plan.id, 
                check_in_date, 
                check_out_date
            )
            
            if 'error' not in pricing:
                comparisons.append({
                    'rate_plan_id': rate_plan.id,
                    'rate_plan_name': rate_plan.name,
                    'rate_type': rate_plan.rate_type,
                    'is_refundable': rate_plan.is_refundable,
                    'total_amount': pricing['total_amount'],
                    'average_per_night': pricing['average_per_night'],
                    'has_discount': pricing['discount_amount'] > 0,
                    'includes_package': pricing['package_value'] > 0,
                })
        
        # Sort by price
        comparisons.sort(key=lambda x: x['total_amount'])
        
        return comparisons
